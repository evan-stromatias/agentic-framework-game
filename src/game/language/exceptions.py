class ActionNotPresentInResponseError(Exception):
    """Raised when no action is present in the response"""


class ResponseIsNoneError(Exception):
    """Raised when the response is `None`"""
