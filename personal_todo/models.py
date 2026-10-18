"""Data classes for the personal to-do list: items and their options."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum

from .exceptions import ValidationError


class Status(Enum):
    """How far through an item the employee is."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(Enum):
    """How important an item is."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def _clean_text(value: str, field_name: str) -> str:
    """Remove spaces from both ends and refuse blank text."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} cannot be blank.")
    return value.strip()


class TodoItem:
    """One item on a personal to-do list."""

    def __init__(self, title: str, description: str = "",
                 deadline: date | None = None,
                 priority: Priority = Priority.MEDIUM) -> None:
        self.id: str = str(uuid.uuid4())
        self.title: str = _clean_text(title, "Title")
        self.description: str = description.strip()
        self.deadline: date | None = deadline
        self.priority: Priority = priority
        self.status: Status = Status.NOT_STARTED
        self.created_at: datetime = datetime.now()
        self.completed_at: datetime | None = None

    def mark_done(self) -> None:
        """Tick the item off and record when."""
        self.status = Status.DONE
        self.completed_at = datetime.now()

    def mark_in_progress(self) -> None:
        """Show the employee has started the item."""
        self.status = Status.IN_PROGRESS
        self.completed_at = None

    def reopen(self) -> None:
        """Put a finished item back to not started."""
        self.status = Status.NOT_STARTED
        self.completed_at = None

    def is_done(self) -> bool:
        """Return True if the item is finished."""
        return self.status is Status.DONE

    def is_overdue(self, today: date | None = None) -> bool:
        """Return True if the deadline has passed and the item isn't done."""
        if self.deadline is None or self.is_done():
            return False
        today = today or date.today()
        return self.deadline < today