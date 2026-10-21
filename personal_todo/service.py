"""The one class the GUI uses to work with personal to-do lists."""

from __future__ import annotations

from datetime import date
from typing import Callable

from .exceptions import AccessDeniedError, ListNotFoundError, ValidationError
from .models import Priority, Status, TodoItem, TodoList

GENERAL_LIST_NAME = "General"


def _list_order(todo_list: TodoList) -> tuple[int, str]:
    """Sort order: General first, then custom lists, then team lists, A to Z."""
    if todo_list.is_general():
        kind = 0
    elif todo_list.is_team_list():
        kind = 2
    else:
        kind = 1
    return kind, todo_list.name.lower()


class PersonalTodoService:
    """Creates, finds and changes employees' personal to-do lists.

    Every method takes the logged-in employee's email first, so one
    employee can never see or change another employee's lists.
    """

    def __init__(self, archive_after_days: int = 30) -> None:
        self._lists: dict[str, TodoList] = {}
        self._archive_after_days = archive_after_days
        self._listeners: list[Callable[[], None]] = []

    # ----- updates for the GUI -----

    def on_change(self, callback: Callable[[], None]) -> None:
        """Register a function to run whenever any list or item changes."""
        self._listeners.append(callback)

    def _notify(self) -> None:
        for callback in self._listeners:
            callback()

    # ----- lists -----

    def get_lists(self, owner_email: str) -> list[TodoList]:
        """Return the employee's lists: General, then custom lists, then teams.

        Creates the General list if it doesn't exist yet, and archives
        items that have been done for longer than the archive period.
        """
        owner = owner_email.strip().lower()
        owned = [todo_list for todo_list in self._lists.values()
                 if todo_list.owner_email == owner]

        if not any(todo_list.is_general() for todo_list in owned):
            general = TodoList(GENERAL_LIST_NAME, owner, general=True)
            self._lists[general.id] = general
            owned.append(general)

        for todo_list in owned:
            todo_list.archive_old_completed(self._archive_after_days)

        return sorted(owned, key=_list_order)

    def get_general_list(self, owner_email: str) -> TodoList:
        """Return the employee's General list."""
        return self.get_lists(owner_email)[0]

    def create_list(self, owner_email: str, name: str) -> TodoList:
        """Create a custom list that isn't tied to a team, e.g. "Training"."""
        if not name or not name.strip():
            raise ValidationError("List name cannot be blank.")
        for todo_list in self.get_lists(owner_email):
            if todo_list.name.lower() == name.strip().lower():
                raise ValidationError(f"You already have a list called {todo_list.name}.")

        new_list = TodoList(name, owner_email)
        self._lists[new_list.id] = new_list
        self._notify()
        return new_list

    def create_team_list(self, owner_email: str, team: str) -> TodoList:
        """Create a list for one team. Each team can only have one list."""
        if not team or not team.strip():
            raise ValidationError("Team name cannot be blank.")
        for todo_list in self.get_lists(owner_email):
            if todo_list.team and todo_list.team.lower() == team.strip().lower():
                raise ValidationError(f"You already have a list for {team.strip()}.")

        new_list = TodoList(team, owner_email, team=team)
        self._lists[new_list.id] = new_list
        self._notify()
        return new_list

    def delete_list(self, owner_email: str, list_id: str) -> None:
        """Delete a team or custom list and its items. General can't be deleted."""
        todo_list = self._get_owned_list(owner_email, list_id)
        if todo_list.is_general():
            raise ValidationError("The General list can't be deleted.")
        del self._lists[list_id]
        self._notify()

    # ----- items -----

    def add_item(self, owner_email: str, list_id: str, title: str,
                 description: str = "", deadline: date | None = None,
                 priority: Priority = Priority.MEDIUM) -> TodoItem:
        """Add a new item to one of the employee's lists."""
        todo_list = self._get_owned_list(owner_email, list_id)
        item = TodoItem(title, description, deadline, priority)
        todo_list.add_item(item)
        self._notify()
        return item

    def update_status(self, owner_email: str, list_id: str, item_id: str,
                      status: Status) -> TodoItem:
        """Change an item's progress: not started, in progress or done."""
        item = self._get_owned_list(owner_email, list_id).get_item(item_id)
        if status is Status.DONE:
            item.mark_done()
        elif status is Status.IN_PROGRESS:
            item.mark_in_progress()
        else:
            item.reopen()
        self._notify()
        return item

    def tick_item(self, owner_email: str, list_id: str, item_id: str) -> TodoItem:
        """Mark an item as done."""
        return self.update_status(owner_email, list_id, item_id, Status.DONE)

    def edit_item(self, owner_email: str, list_id: str, item_id: str,
                  title: str | None = None, description: str | None = None,
                  deadline: date | None = None,
                  priority: Priority | None = None) -> TodoItem:
        """Change any of an item's details. Anything left as None stays the same."""
        item = self._get_owned_list(owner_email, list_id).get_item(item_id)
        if title is not None:
            if not title.strip():
                raise ValidationError("Title cannot be blank.")
            item.title = title.strip()
        if description is not None:
            item.description = description.strip()
        if deadline is not None:
            item.deadline = deadline
        if priority is not None:
            item.priority = priority
        self._notify()
        return item

    def delete_item(self, owner_email: str, list_id: str, item_id: str) -> None:
        """Delete an item from one of the employee's lists."""
        self._get_owned_list(owner_email, list_id).remove_item(item_id)
        self._notify()

    # ----- views across all lists -----

    def get_all_items(self, owner_email: str) -> list[TodoItem]:
        """Every current item across all the employee's lists."""
        return [item for todo_list in self.get_lists(owner_email)
                for item in todo_list.items()]

    def get_overdue_items(self, owner_email: str,
                          today: date | None = None) -> list[TodoItem]:
        """Items past their deadline that aren't done."""
        return [item for item in self.get_all_items(owner_email)
                if item.is_overdue(today)]

    # ----- private helpers -----

    def _get_owned_list(self, owner_email: str, list_id: str) -> TodoList:
        """Find a list and check it belongs to this employee."""
        todo_list = self._lists.get(list_id)
        if todo_list is None:
            raise ListNotFoundError(f"No list with ID {list_id}.")
        if todo_list.owner_email != owner_email.strip().lower():
            raise AccessDeniedError("You can only change your own to-do lists.")
        return todo_list