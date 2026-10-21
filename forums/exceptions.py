"""Errors raised by the forums component."""


class ForumError(Exception):
    """Base class for every error in this component."""


class ValidationError(ForumError, ValueError):
    """A value is missing or invalid, such as a blank post title."""


class TopicNotFoundError(ForumError):
    """No topic has the given ID."""


class PostNotFoundError(ForumError):
    """No post has the given ID, or the post has been removed."""


class CommentNotFoundError(ForumError):
    """The post has no comment with the given ID."""


class AccessDeniedError(ForumError):
    """The user isn't allowed to do this, such as removing someone else's post."""