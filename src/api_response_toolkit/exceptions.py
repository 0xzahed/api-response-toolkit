"""Custom exception classes for the api-response-toolkit package.

Each exception carries structured information (message, code, status_code,
errors, details, metadata) so that middleware and exception handlers can
produce consistent API responses without additional translation.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .errors import code_for_status
from .types import ErrorMapping

DEFAULT_MESSAGE = "An error occurred."


class APIException(Exception):
    """Base class for all toolkit API exceptions.

    Attributes:
        message: Human-readable error message.
        code: Machine-readable error code.
        status_code: HTTP status code associated with the error.
        errors: Optional mapping of field-level errors.
        details: Optional extra error details.
        metadata: Optional metadata mapping.
    """

    default_message: str = DEFAULT_MESSAGE
    default_code: str = "API_ERROR"
    default_status_code: int = 500

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        status_code: int | None = None,
        errors: ErrorMapping | None = None,
        details: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.message = message if message is not None else self.default_message
        self.code = code if code is not None else self.default_code
        self.status_code = status_code if status_code is not None else self.default_status_code
        self.errors: dict[str, Any] | None = dict(errors) if errors is not None else None
        self.details = details
        self.metadata: dict[str, Any] | None = dict(metadata) if metadata is not None else None
        super().__init__(self.message)

    def to_payload(self) -> dict[str, Any]:
        """Convert the exception to a response payload dictionary."""
        payload: dict[str, Any] = {
            "success": False,
            "message": self.message,
            "code": self.code,
        }
        if self.errors is not None:
            payload["errors"] = self.errors
        if self.details is not None:
            payload["details"] = self.details
        if self.metadata is not None:
            payload["meta"] = self.metadata
        return payload


class NotFoundError(APIException):
    """Raised when a requested resource cannot be found (HTTP 404)."""

    default_message = "Resource not found"
    default_code = "NOT_FOUND"
    default_status_code = 404


class UnauthorizedError(APIException):
    """Raised when authentication is required and has failed (HTTP 401)."""

    default_message = "Authentication credentials were not provided or are invalid."
    default_code = "UNAUTHORIZED"
    default_status_code = 401


class ForbiddenError(APIException):
    """Raised when the user does not have permission (HTTP 403)."""

    default_message = "You do not have permission to perform this action."
    default_code = "FORBIDDEN"
    default_status_code = 403


class ValidationError(APIException):
    """Raised when input validation fails (HTTP 400)."""

    default_message = "Validation failed"
    default_code = "VALIDATION_ERROR"
    default_status_code = 400

    def __init__(
        self,
        message: str | None = None,
        errors: ErrorMapping | None = None,
        code: str | None = None,
        details: Any = None,
        metadata: Mapping[str, Any] | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            errors=errors,
            details=details,
            metadata=metadata,
        )


class BadRequestError(APIException):
    """Raised for generic malformed requests (HTTP 400)."""

    default_message = "Bad request"
    default_code = "BAD_REQUEST"
    default_status_code = 400


class ConflictError(APIException):
    """Raised when a request conflicts with the current state (HTTP 409)."""

    default_message = "Conflict"
    default_code = "CONFLICT"
    default_status_code = 409


class InternalServerError(APIException):
    """Raised for unexpected internal errors (HTTP 500)."""

    default_message = "Internal server error"
    default_code = "INTERNAL_ERROR"
    default_status_code = 500


def from_status_code(
    status_code: int,
    message: str | None = None,
    errors: ErrorMapping | None = None,
    details: Any = None,
    metadata: Mapping[str, Any] | None = None,
) -> APIException:
    """Construct an appropriate :class:`APIException` subclass for a status code.

    This is a convenience factory that maps common HTTP status codes to the
    most specific exception subclass available.

    Args:
        status_code: The HTTP status code.
        message: Optional message override.
        errors: Optional field-level errors.
        details: Optional extra details.
        metadata: Optional metadata.

    Returns:
        An instance of the most specific matching exception subclass.
    """
    code = code_for_status(status_code)
    kwargs: dict[str, Any] = {
        "message": message,
        "code": code,
        "status_code": status_code,
        "errors": errors,
        "details": details,
        "metadata": metadata,
    }
    mapping: Mapping[int, type[APIException]] = {
        400: BadRequestError,
        401: UnauthorizedError,
        403: ForbiddenError,
        404: NotFoundError,
        409: ConflictError,
        500: InternalServerError,
    }
    cls = mapping.get(status_code, APIException)
    return cls(**kwargs)


__all__ = [
    "APIException",
    "BadRequestError",
    "ConflictError",
    "ForbiddenError",
    "InternalServerError",
    "NotFoundError",
    "UnauthorizedError",
    "ValidationError",
    "from_status_code",
]
