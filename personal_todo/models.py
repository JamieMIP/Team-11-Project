"""Data classes for the personal to-do list: items and their options."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from enum import Enum

from .exceptions import ItemNotFoundError, ValidationError


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


class TodoList:
    """A group of to-do items belonging to one employee.

    A list with a team (e.g. "Team X") holds items for that team.
    A list with no team is the employee's General list for loose items.
    """

    def __init__(self, name: str, owner_email: str,
                 team: str | None = None) -> None:
        self.id: str = str(uuid.uuid4())
        self.name: str = _clean_text(name, "List name")
        self.owner_email: str = _clean_text(owner_email, "Owner email").lower()
        self.team: str | None = team.strip() if team and team.strip() else None
        self.created_at: datetime = datetime.now()
        self._items: list[TodoItem] = []
        self._archived: list[TodoItem] = []

    def is_general(self) -> bool:
        """Return True if this is the General list (no team)."""
        return self.team is None

    def add_item(self, item: TodoItem) -> None:
        """Add an item to the end of the list."""
        self._items.append(item)

    def get_item(self, item_id: str) -> TodoItem:
        """Find an item by its ID."""
        for item in self._items:
            if item.id == item_id:
                return item
        raise ItemNotFoundError(f"No item with ID {item_id} in list '{self.name}'.")

    def remove_item(self, item_id: str) -> None:
        """Delete an item from the list."""
        item = self.get_item(item_id)
        self._items.remove(item)

    def items(self) -> list[TodoItem]:
        """Return all current items, in the order they were added."""
        return list(self._items)

    def rename(self, new_name: str) -> None:
        """Change the list's name."""
        self.name = _clean_text(new_name, "List name")

    def progress(self) -> float:
        """Return the percentage of current items done, from 0 to 100."""
        if not self._items:
            return 0.0
        done = sum(1 for item in self._items if item.is_done())
        return round(done / len(self._items) * 100, 1)

    def archive_old_completed(self, days: int = 30,
                              now: datetime | None = None) -> list[TodoItem]:
        """Move items that have been done for more than `days` days into the archive.

        Returns the items that were archived, so the GUI can tell the user.
        """
        now = now or datetime.now()
        cutoff = now - timedelta(days=days)
        old_items = [item for item in self._items
                     if item.is_done() and item.completed_at is not None
                     and item.completed_at < cutoff]
        for item in old_items:
            self._items.remove(item)
            self._archived.append(item)
        return old_items

    def archived_items(self) -> list[TodoItem]:
        """Return all archived items."""
        return list(self._archived)