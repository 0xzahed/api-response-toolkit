"""DRF response helpers returning DRF ``Response`` objects.

These mirror the core :mod:`api_response_toolkit.response` API but return
``rest_framework.response.Response`` instances with the correct status code.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from rest_framework.response import Response

from ..response import (
    build_pagination,
    to_dict,
)
from ..response import (
    error as _error,
)
from ..response import (
    success as _success,
)
from ..response import (
    validation_error as _validation_error,
)
from ..types import ErrorMapping, ResponsePayload


def _to_response(payload: ResponsePayload) -> Response:
    """Serialize a :class:`ResponsePayload` to a DRF ``Response``."""
    return Response(to_dict(payload), status=payload.status_code)


def success(
    data: Any = None,
    message: str | None = None,
    status_code: int = 200,
    meta: Mapping[str, Any] | None = None,
    pagination: Mapping[str, Any] | None = None,
) -> Response:
    """Build a DRF ``Response`` for a success response.

    Args:
        data: The response data.
        message: Optional success message.
        status_code: HTTP status code (2xx).
        meta: Optional metadata mapping.
        pagination: Optional pagination mapping.

    Returns:
        A :class:`rest_framework.response.Response` with the standardized body.
    """
    payload = _success(
        data=data,
        message=message,
        status_code=status_code,
        meta=meta,
        pagination=pagination,
    )
    return _to_response(payload)


def error(
    message: str | None = None,
    code: str | None = None,
    status_code: int = 400,
    data: Any = None,
    errors: ErrorMapping | None = None,
    details: Any = None,
    meta: Mapping[str, Any] | None = None,
) -> Response:
    """Build a DRF ``Response`` for an error response."""
    payload = _error(
        message=message,
        code=code,
        status_code=status_code,
        data=data,
        errors=errors,
        details=details,
        meta=meta,
    )
    return _to_response(payload)


def validation_error(
    errors: ErrorMapping,
    message: str = "Validation failed",
    code: str = "VALIDATION_ERROR",
    status_code: int = 400,
    details: Any = None,
    meta: Mapping[str, Any] | None = None,
) -> Response:
    """Build a DRF ``Response`` for a validation error response."""
    payload = _validation_error(
        errors=errors,
        message=message,
        code=code,
        status_code=status_code,
        details=details,
        meta=meta,
    )
    return _to_response(payload)


def paginated(
    data: Any = None,
    page: int = 1,
    limit: int = 20,
    total: int = 0,
    message: str | None = None,
    status_code: int = 200,
    meta: Mapping[str, Any] | None = None,
) -> Response:
    """Build a DRF ``Response`` for a paginated success response."""
    pagination = build_pagination(page=page, limit=limit, total=total)
    payload = _success(
        data=data,
        message=message,
        status_code=status_code,
        meta=meta,
        pagination=pagination,
    )
    return _to_response(payload)


__all__ = [
    "error",
    "paginated",
    "success",
    "validation_error",
]
