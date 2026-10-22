"""The one class the GUI uses to work with the forums."""

from __future__ import annotations

from typing import Callable

from .exceptions import (AccessDeniedError, PostNotFoundError,
                         TopicNotFoundError, ValidationError)
from .forum_feed import FeedEntry, FeedRanker
from .forum_models import (Announcement, Comment, ForumPost, Post, Topic,
                           TopicCategory)


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

    # ----- FOLLOWING TOPICS -----

    def follow_topic(self, user_email: str, topic_id: str) -> None:
        """Follow a topic so its posts rank higher in the user's feed."""
        topic = self.get_topic(topic_id)
        self._followed.setdefault(self._key(user_email), set()).add(topic.id)
        self._notify()

    def unfollow_topic(self, user_email: str, topic_id: str) -> None:
        """Stop following a topic. Does nothing if it wasn't followed."""
        self._followed.get(self._key(user_email), set()).discard(topic_id)
        self._notify()

    def is_following(self, user_email: str, topic_id: str) -> bool:
        """Return True if the user follows this topic."""
        return topic_id in self._followed_ids(user_email)

    def get_followed_topics(self, user_email: str) -> list[Topic]:
        """Return the topics the user follows, A to Z."""
        followed = self._followed_ids(user_email)
        return [topic for topic in self.get_topics() if topic.id in followed]

    # ----- POSTS -----

    def create_forum_post(self, user_email: str, user_name: str, topic_id: str,
                          title: str, body: str,
                          tags: list[str] | None = None) -> ForumPost:
        """Publish a forum post that people can comment on and solve."""
        topic = self.get_topic(topic_id)
        post = ForumPost(title, body, user_email, user_name, topic, tags)
        self._add_post(post)
        return post

    def create_announcement(self, user_email: str, user_name: str, topic_id: str,
                            title: str, description: str,
                            is_moderator: bool = False) -> Announcement:
        """Publish an announcement (title and description only). Moderators means Managers or Team Leaders."""
        if not is_moderator:
            raise AccessDeniedError("Only managers and team leaders can post announcements.")
        topic = self.get_topic(topic_id)
        announcement = Announcement(title, description, user_email, user_name, topic)
        self._add_post(announcement)
        return announcement

    def _add_post(self, post: Post) -> None:
        """Store a new post of any kind and tell the GUI."""
        self._posts[post.id] = post
        self._notify()

    def _get_forum_post(self, post_id: str) -> ForumPost:
        """Find a post and check it is a forum post, which can have solutions."""
        post = self.get_post(post_id)
        if not isinstance(post, ForumPost):
            raise ValidationError(f"{post.type_label()}s can't have a solution.")
        return post

    def get_post(self, post_id: str) -> Post:
        """Find a post to open. Removed posts count as not found."""
        post = self._posts.get(post_id)
        if post is None or post.is_removed:
            raise PostNotFoundError("This post doesn't exist or has been removed.")
        return post

    def get_all_posts(self) -> list[Post]:
        """Every post that hasn't been removed, newest first.

        This is what the search feature should search through.
        """
        visible = [post for post in self._posts.values() if not post.is_removed]
        return sorted(visible, key=lambda post: post.created_at, reverse=True)

    def remove_post(self, user_email: str, post_id: str,
                    is_moderator: bool = False) -> None:
        """Remove a post. Authors can remove their own, moderators any."""
        self.get_post(post_id).remove(user_email, is_moderator)
        self._notify()

    # ----- COMMENTS AND SOLUTIONS -----

    def add_comment(self, user_email: str, user_name: str, post_id: str,
                    body: str) -> Comment:
        """Reply to a post and return the new comment."""
        comment = self.get_post(post_id).add_comment(user_email, user_name, body)
        self._notify()
        return comment

    def mark_solution(self, user_email: str, post_id: str, comment_id: str) -> Comment:
        """Mark a comment as the accepted solution. Only the post's author can."""
        comment = self._get_forum_post(post_id).mark_solution(user_email, comment_id)
        self._notify()
        return comment

    def clear_solution(self, user_email: str, post_id: str) -> None:
        """Remove the accepted solution mark. Only the post's author can."""
        self._get_forum_post(post_id).clear_solution(user_email)
        self._notify()

    # ----- INSIGHT FOR MANAGERS -----

    def unsolved_by_topic(self) -> list[tuple[Topic, int]]:
        """Count unsolved technical posts in each topic, most first.

        Counts are per topic, never per person, so this can't be used
        to target individuals. Topics with nothing unsolved are left out.
        """
        counts: list[tuple[Topic, int]] = []
        for topic in self.get_topics():
            if not topic.is_technical():
                continue
            unsolved = sum(1 for post in self.get_all_posts()   
                           if post.topic is topic and not post.needs_answer())
            if unsolved:
                counts.append((topic, unsolved))
        counts.sort(key=lambda count: count[1], reverse=True)
        return counts

    # ----- PRIVATE HELPERS -----

    def _key(self, user_email: str) -> str:
        """Tidy an email so the same person always matches."""
        return user_email.strip().lower()

    def _followed_ids(self, user_email: str) -> set[str]:
        """Return a copy of the IDs of the topics this user follows."""
        return set(self._followed.get(self._key(user_email), set()))