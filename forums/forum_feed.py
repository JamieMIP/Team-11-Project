"""Builds the ranked posts feed shown on the home page.

Each post gets a score from three parts: how relevant its topic is to
the user, how much discussion it has, and whether it is an unsolved
technical question. The total is multiplied by a freshness value that
halves every few days, so old posts sink unless someone comments again.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta

from .forum_models import Post

class FeedEntry:
    """One post in the feed, with its score and why it was shown.

    The GUI shows the reason as a small label, e.g. "From a topic you follow".
    """

    def __init__(self, post: Post, score: float, reason: str) -> None:
        self.post: Post = post
        self.score: float = score
        self.reason: str = reason
    
class FeedRanker:
    """Chooses and orders the posts each user sees.
        
    Essentially a scoring function that takes a post and returns a number."""

    FOLLOWED_WEIGHT: float = 3.0
    TEAM_WEIGHT: float = 2.0
    ACTIVITY_WEIGHT: float = 0.5
    UNSOLVED_BOOST: float = 1.0
    RECENCY_HALF_LIFE_DAYS: float = 3.0
    COLD_START_DAYS: int = 14

    def build_feed(self, posts: list[Post], followed_topic_ids: set[str],
                   team_names: list[str], limit: int = 20,
                   now: datetime | None = None) -> list[FeedEntry]:
        """Return the user's home feed, best match first."""
        now = now or datetime.now()
        visible = [post for post in posts if not post.is_removed]
        candidates = self._gather_candidates(visible, followed_topic_ids,
                                             team_names, now)
        return self.rank(candidates, followed_topic_ids, team_names, limit, now)

    def rank(self, posts: list[Post], followed_topic_ids: set[str],
             team_names: list[str], limit: int = 20,
             now: datetime | None = None) -> list[FeedEntry]:
        """Score the given posts and return them best first.

        Used directly for the browse-by-topic view, where the posts have
        already been narrowed down to one topic.
        """
        now = now or datetime.now()
        entries = [self._score(post, followed_topic_ids, team_names, now)
                   for post in posts if not post.is_removed]
        entries.sort(key=lambda entry: (entry.score, entry.post.last_activity()),
                     reverse=True)
        return entries[:limit]


        # ----- PRIVATE HELPERS -----

    def _gather_candidates(self, posts: list[Post], followed_topic_ids: set[str],
                           team_names: list[str], now: datetime) -> list[Post]:
        """Pick the posts worth scoring for this user."""
        if followed_topic_ids:
            matching = [post for post in posts
                        if post.topic.id in followed_topic_ids
                        or post.topic.is_linked_to(team_names)]
            if matching:
                return matching
        # Cold start: the user follows nothing (or their topics are empty),
        # so show recent posts from across the company instead.
        cutoff = now - timedelta(days=self.COLD_START_DAYS)
        recent = [post for post in posts if post.last_activity() >= cutoff]
        return recent or posts

    def _score(self, post: Post, followed_topic_ids: set[str],
               team_names: list[str], now: datetime) -> FeedEntry:
        """Work out one post's score and the biggest reason behind it."""
        topic_score = 0.0
        topic_reason = ""
        if post.topic.id in followed_topic_ids:
            topic_score = self.FOLLOWED_WEIGHT
            topic_reason = "From a topic you follow"
        elif post.topic.is_linked_to(team_names):
            topic_score = self.TEAM_WEIGHT
            topic_reason = "From your team's topics"

        activity_score = self.ACTIVITY_WEIGHT * math.log(1 + post.comment_count())

        unsolved_score = 0.0
        if post.topic.is_technical() and not post.is_solved():
            unsolved_score = self.UNSOLVED_BOOST

        age_days = max(0.0, (now - post.last_activity()).total_seconds() / 86400)
        freshness = 0.5 ** (age_days / self.RECENCY_HALF_LIFE_DAYS)

        score = (1 + topic_score + activity_score + unsolved_score) * freshness

        parts = [
            (topic_score, topic_reason),
            (unsolved_score, f"Unsolved in {post.topic.name}"),
            (activity_score, "Active discussion"),
        ]
        best_value, best_reason = max(parts, key=lambda part: part[0])
        if best_value == 0:
            best_reason = f"Recent in {post.topic.name}"
        return FeedEntry(post, score, best_reason)