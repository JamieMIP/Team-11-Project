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