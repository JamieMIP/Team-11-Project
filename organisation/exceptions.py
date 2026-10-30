"""Errors raised by the organisation package.

The GUI can catch OrgError (the base class) and show str(error) to the
user in a message box instead of the app crashing.
"""


class OrgError(Exception):
    """Base class for every error in this package."""


class PermissionDenied(OrgError):
    """The logged-in user is not allowed to do this."""


class NotFound(OrgError):
    """No employee, team, project or task has that ID or email."""


class InvalidAction(OrgError, ValueError):
    """The request breaks a rule, e.g. a blank name or a duplicate member."""
