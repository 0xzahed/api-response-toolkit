"""Common error code constants and helper utilities.

These string constants provide a consistent vocabulary for machine-readable
error codes across an application. They are entirely optional — callers may
use any string for the ``code`` field.
"""

from __future__ import annotations

from collections.abc import Mapping

# ---------------------------------------------------------------------------
# Standard error code constants
# ---------------------------------------------------------------------------

VALIDATION_ERROR = "VALIDATION_ERROR"
NOT_FOUND = "NOT_FOUND"
UNAUTHORIZED = "UNAUTHORIZED"
FORBIDDEN = "FORBIDDEN"
BAD_REQUEST = "BAD_REQUEST"
CONFLICT = "CONFLICT"
INTERNAL_ERROR = "INTERNAL_ERROR"
NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
RATE_LIMITED = "RATE_LIMITED"
TIMEOUT = "TIMEOUT"
PARSE_ERROR = "PARSE_ERROR"
METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"

# Mapping of common HTTP status codes to default error codes.
STATUS_CODE_TO_CODE: Mapping[int, str] = {
    400: BAD_REQUEST,
    401: UNAUTHORIZED,
    403: FORBIDDEN,
    404: NOT_FOUND,
    405: METHOD_NOT_ALLOWED,
    408: TIMEOUT,
    409: CONFLICT,
    415: UNSUPPORTED_MEDIA_TYPE,
    429: RATE_LIMITED,
    500: INTERNAL_ERROR,
    501: NOT_IMPLEMENTED,
    503: SERVICE_UNAVAILABLE,
}


def code_for_status(status_code: int) -> str:
    """Return a sensible default error code for an HTTP status code.

    Falls back to :data:`INTERNAL_ERROR` for unknown 5xx codes and
    :data:`BAD_REQUEST` for unknown 4xx codes.

    Args:
        status_code: An HTTP status code.

    Returns:
        A machine-readable error code string.
    """
    code = STATUS_CODE_TO_CODE.get(status_code)
    if code is not None:
        return code
    if 500 <= status_code <= 599:
        return INTERNAL_ERROR
    return BAD_REQUEST


__all__ = [
    "BAD_REQUEST",
    "CONFLICT",
    "FORBIDDEN",
    "INTERNAL_ERROR",
    "METHOD_NOT_ALLOWED",
    "NOT_FOUND",
    "NOT_IMPLEMENTED",
    "PARSE_ERROR",
    "RATE_LIMITED",
    "SERVICE_UNAVAILABLE",
    "STATUS_CODE_TO_CODE",
    "TIMEOUT",
    "UNAUTHORIZED",
    "UNSUPPORTED_MEDIA_TYPE",
    "VALIDATION_ERROR",
    "code_for_status",
]
