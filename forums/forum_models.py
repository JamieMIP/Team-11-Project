"""Data classes for the forums: people, topics, posts and comments.

Role, Permission, User and Team are stand-ins until the team's shared
user model exists. They only hold what the forums need, so they can be
swapped for the shared classes later by changing the imports.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from enum import Enum
from .exceptions import AccessDeniedError, CommentNotFoundError, ValidationError

class TopicCategory(Enum):
    """Determines whether a topic holds technical or non-technical knowledge"""

    TECHNICAL = "technical"
    NON_TECHNICAL = "non-technical"


"""Cleaners to check for staff email addresses, can be set to refuse if it is not a specific domain"""

def _clean_text(value: str, field_name: str) -> str:
    """Remove spaces from both ends and refuse blank text"""

    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} cannot be blank.")
    return value.strip()

def _clean_email(value: str) -> str:
    """Lower-case a staff email and refuse anything without an @"""

    email = _clean_text(value, "Email").lower()
    if "@" not in email:
        raise ValidationError("Email must be a staff email address.")
    return email

def _plain_text(text: str) -> str:
    """Remove Markdown symbols so a body can be searched or previewed.

    [the guide](https://...) keeps only "the guide", and the symbols
    from **bold**, *italic*, `code`, # headings and > quotes are dropped.
    """
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s*[#>]+\s*", "", text, flags=re.MULTILINE)
    text = text.replace("*", "").replace("`", "")
    return " ".join(text.split())

def _clean_tags(tags: list[str]) -> list[str]:
    """Lower-case tags, drop a leading # and remove blanks and repeats."""
    cleaned: list[str] = []
    for tag in tags:
        tag = tag.strip().lstrip("#").strip().lower()
        if tag and tag not in cleaned:
            cleaned.append(tag)
    return cleaned

# ----- CLASSES -----

class Topic:
    """A subject that posts are filed under, such as "Printing" Used for filtering later."""

    def __init__(self, name: str, created_by: str, description: str = "",
                 category: TopicCategory = TopicCategory.TECHNICAL) -> None:
        self.id: str = str(uuid.uuid4())
        self.name: str = _clean_text(name, "Topic name")
        self.created_by: str = _clean_email(created_by)
        self.description: str = description.strip()
        self.category: TopicCategory = category
        self.created_at: datetime = datetime.now()
        self._teams: list[str] = []

    def is_technical(self) -> bool:
        """Return True for technical topics (configs, bugs, fixes)."""
        return self.category is TopicCategory.TECHNICAL

    def teams(self) -> list[str]:
        """Return the names of the teams this topic is linked to."""
        return list(self._teams)

    def link_team(self, team: str) -> None:
        """Link a team so its members see this topic's posts in their feed."""
        team = _clean_text(team, "Team name")
        if not self.is_linked_to([team]):
            self._teams.append(team)

    def unlink_team(self, team: str) -> None:
        """Stop showing this topic to a team. Does nothing if it wasn't linked."""
        self._teams = [linked for linked in self._teams
                       if linked.lower() != team.strip().lower()]

    def is_linked_to(self, team_names: list[str]) -> bool:
        """Return True if any of these teams is linked to the topic."""
        wanted = {name.strip().lower() for name in team_names}
        return any(linked.lower() in wanted for linked in self._teams)

class Comment:
    """A reply underneath a post."""

    def __init__(self, author_email: str, author_name: str, body: str,
                 created_at: datetime | None = None) -> None:
        self.id: str = str(uuid.uuid4())
        self.author_email: str = _clean_email(author_email)
        self.author_name: str = _clean_text(author_name, "Author name")
        self.body: str = _clean_text(body, "Comment body")
        self.created_at: datetime = created_at or datetime.now()

    def plain_text(self) -> str:
        """Return the comment without formatting."""
        return _plain_text(self.body)

class Post:
    """A piece of shared knowledge inside a topic.

    The body is rich text (HTML from the editor), so it can hold
    formatting and links. created_at can be passed in so sample data
    can have posts of different ages; normally leave it out.
    """

    def __init__(self, title: str, body: str, author_email: str,
                 author_name: str, topic: Topic,
                 tags: list[str] | None = None,
                 created_at: datetime | None = None) -> None:
        if topic is None:
            raise ValidationError("Choose a topic for the post.")
        self.id: str = str(uuid.uuid4())
        self.title: str = _clean_text(title, "Title")
        self.body: str = _clean_text(body, "Body")
        self.author_email: str = _clean_email(author_email)
        self.author_name: str = _clean_text(author_name, "Author name")
        self.topic: Topic = topic
        self.tags: list[str] = _clean_tags(tags or [])
        self.created_at: datetime = created_at or datetime.now()
        self.accepted_solution: Comment | None = None
        self.is_removed: bool = False
        self.removed_by: str | None = None
        self.removed_at: datetime | None = None
        self._comments: list[Comment] = []


    # ----- COMMENTS -----

    def add_comment(self, author_email: str, author_name: str, body: str, created_at: datetime | None = None) -> Comment:
        """Add a comment to a post and return it"""
        if self.is_removed:
            raise AccessDeniedError("Cannot comment on a removed post.")
        comment = Comment(author_email, author_name, body, created_at)
        self._comments.append(comment)
        return comment

    def get_comment(self, comment_id: str) -> Comment:
        """Return a comment by its ID, or raise CommentNotFoundError."""
        for comment in self._comments:
            if comment.id == comment_id:
                return comment
        raise CommentNotFoundError(f"No comment with ID {comment_id}.")

    def comments(self) -> list[Comment]:
        """Return all comments on this post, oldest first"""
        return list(self._comments)

    def comment_count(self) -> int:
        """Return the number of comments on this post"""
        return len(self._comments)

    # ----- ACCEPTED SOLUTION -----
    """ Since forums usually are questions that are asked, this will mark the accepted solution by the author"""

    def is_author(self, user_email: str) -> bool:
        """Return True if the given email is the post's author."""
        return user_email.strip().lower() == self.author_email.lower()

    def mark_solution(self, user_email: str, comment_id: str) -> None:
        """Mark a comment as the accepted solution to the post.

        Only the post's author can mark a solution. If the comment ID is
        invalid, raise CommentNotFoundError.
        """
        if not self.is_author(user_email):
            raise AccessDeniedError("Only the post's author can mark a solution.")
        self.accepted_solution = self.get_comment(comment_id)
        return self.accepted_solution

    def clear_solution(self, user_email: str) -> None:
        """Clear the accepted solution.

        Only the post's author can clear a solution. If there is no
        accepted solution, this does nothing.
        """
        if not self.is_author(user_email):
            raise AccessDeniedError("Only the post's author can clear a solution.")
        self.accepted_solution = None

    def is_solved(self) -> bool:
        """Return True if the post has an accepted solution."""
        return self.accepted_solution is not None

    # ----- REMOVE POSTS -----

    def can_be_removed_by(self, user_email: str, is_moderator: bool = False) -> bool:
        """Return True if the given email is allowed to remove this post."""

        return is_moderator or self.is_author(user_email)

    def remove(self, user_email: str, is_moderator: bool = False) -> None:
        """Return True is person can remove the post
        Authors can remove their own posts and moderators can remove any

        The post is kept, with who removed it and when, in case removal is questioned
        """
        if not self.can_be_removed_by(user_email, is_moderator):
            raise AccessDeniedError("You cannot remove this post.")
        if not self.is_removed:
            self.is_removed = True
            self.removed_by = user_email.strip().lower()
            self.removed_at = datetime.now()

    # ----- POST HELPERS -----

    def last_activity(self) -> datetime:
        """Return when the post was written or last commented on."""
        if not self._comments:
            return self.created_at
        return max(self.created_at,
                   max(comment.created_at for comment in self._comments))

    def plain_text(self) -> str:
        """Return the body without formatting, for searching."""
        return _plain_text(self.body)

    def preview(self, length: int = 150) -> str:
        """Return the start of the body as plain text, for feed cards."""
        text = self.plain_text()
        if len(text) <= length:
            return text
        return text[:length].rsplit(" ", 1)[0] + "..."