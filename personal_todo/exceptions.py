"""Errors raised by the personal to-do list component."""


class TodoError(Exception):
    """Base class for every error in this component."""


class ValidationError(TodoError, ValueError):
    """A value is missing or invalid, such as a blank title."""


class ListNotFoundError(TodoError):
    """No to-do list has the given ID."""


class ItemNotFoundError(TodoError):
    """No item in the list has the given ID."""


class AccessDeniedError(TodoError):
    """The list belongs to a different employee."""