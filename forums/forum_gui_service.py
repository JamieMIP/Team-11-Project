"""The one class the GUI uses to work with the forums."""

from __future__ import annotations

from typing import Callable

from .exceptions import (AccessDeniedError, PostNotFoundError,
                         TopicNotFoundError, ValidationError)
from .feed import FeedEntry, FeedRanker
from .models import Comment, Post, Topic, TopicCategory


class ForumService:
    """Creates, finds and changes topics, posts and comments.

    Every method that acts for someone takes the logged-in user's email
    first. Roles and teams belong to other parts of the system, so the
    GUI passes in is_moderator and the user's team names when needed.
    """

    def __init__(self) -> None:
        self._topics: dict[str, Topic] = {}
        self._posts: dict[str, Post] = {}
        self._followed: dict[str, set[str]] = {}
        self._ranker = FeedRanker()
        self._listeners: list[Callable[[], None]] = []

    # ----- UPDATES FOR GUI -----

    def on_change(self, callback: Callable[[], None]) -> None:
        """Register a function to run whenever a topic, post or comment changes."""
        self._listeners.append(callback)

    def _notify(self) -> None:
        for callback in self._listeners:
            callback()

    # ----- FEED -----

    def get_home_feed(self, user_email: str, team_names: list[str] | None = None,
                      limit: int = 20) -> list[FeedEntry]:
        """Return the ranked posts for the user's home page."""
        return self._ranker.build_feed(list(self._posts.values()),
                                       self._followed_ids(user_email),
                                       team_names or [], limit)

    def get_topic_feed(self, user_email: str, topic_id: str,
                       team_names: list[str] | None = None,
                       limit: int = 20) -> list[FeedEntry]:
        """Return the ranked posts in one topic (browse by topic)."""
        topic = self.get_topic(topic_id)
        posts = [post for post in self._posts.values() if post.topic is topic]
        return self._ranker.rank(posts, self._followed_ids(user_email),
                                 team_names or [], limit)

    # ----- TOPICS -----

    def get_topics(self) -> list[Topic]:
        """Return every topic, A to Z, for menus and drop-downs."""
        return sorted(self._topics.values(), key=lambda topic: topic.name.lower())

    def get_topic(self, topic_id: str) -> Topic:
        """Find a topic by its ID."""
        topic = self._topics.get(topic_id)
        if topic is None:
            raise TopicNotFoundError(f"No topic with ID {topic_id}.")
        return topic

    def create_topic(self, user_email: str, name: str, description: str = "",
                     category: TopicCategory = TopicCategory.TECHNICAL,
                     is_moderator: bool = False) -> Topic:
        """Add a new topic. Only moderators can."""
        if not is_moderator:
            raise AccessDeniedError("Only moderators can create topics.")
        for topic in self._topics.values():
            if topic.name.lower() == name.strip().lower():
                raise ValidationError(f"A topic called {topic.name} already exists.")
        topic = Topic(name, user_email, description, category)
        self._topics[topic.id] = topic
        self._notify()
        return topic

    def link_topic_to_team(self, topic_id: str, team: str,
                           is_moderator: bool = False) -> Topic:
        """Show a topic's posts to a team in their feed. Only moderators can."""
        if not is_moderator:
            raise AccessDeniedError("Only moderators can link topics to teams.")
        topic = self.get_topic(topic_id)
        topic.link_team(team)
        self._notify()
        return topic