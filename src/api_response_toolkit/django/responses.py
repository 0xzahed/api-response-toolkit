"""Django response helpers returning ``JsonResponse`` objects.

These mirror the core :mod:`api_response_toolkit.response` API but return
Django ``JsonResponse`` instances with the correct status code and content
type.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.http import JsonResponse

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


def _serialize(payload: ResponsePayload) -> JsonResponse:
    """Serialize a :class:`ResponsePayload` to a Django ``JsonResponse``.

    The toolkit always wraps responses in a top-level dict, so ``safe=True``
    (the default) is correct regardless of the ``data`` value.
    """
    body = to_dict(payload)
    return JsonResponse(
        body,
        status=payload.status_code,
        json_dumps_params={"ensure_ascii": False},
    )


def success(
    data: Any = None,
    message: str | None = None,
    status_code: int = 200,
    meta: Mapping[str, Any] | None = None,
    pagination: Mapping[str, Any] | None = None,
) -> JsonResponse:
    """Build a Django ``JsonResponse`` for a success response.

    Args:
        data: The response data. When this is a list, ``safe=False`` is used
            so the top-level JSON can be an array-like structure (the toolkit
            always wraps in an object, so ``safe`` is only relaxed for the
            inner ``data``).
        message: Optional success message.
        status_code: HTTP status code (2xx).
        meta: Optional metadata mapping.
        pagination: Optional pagination mapping.

    Returns:
        A :class:`django.http.JsonResponse` with the standardized body.
    """
    payload = _success(
        data=data,
        message=message,
        status_code=status_code,
        meta=meta,
        pagination=pagination,
    )
    return _serialize(payload)


def error(
    message: str | None = None,
    code: str | None = None,
    status_code: int = 400,
    data: Any = None,
    errors: ErrorMapping | None = None,
    details: Any = None,
    meta: Mapping[str, Any] | None = None,
) -> JsonResponse:
    """Build a Django ``JsonResponse`` for an error response.

    See :func:`api_response_toolkit.response.error` for argument details.
    """
    payload = _error(
        message=message,
        code=code,
        status_code=status_code,
        data=data,
        errors=errors,
        details=details,
        meta=meta,
    )
    return _serialize(payload)


def validation_error(
    errors: ErrorMapping,
    message: str = "Validation failed",
    code: str = "VALIDATION_ERROR",
    status_code: int = 400,
    details: Any = None,
    meta: Mapping[str, Any] | None = None,
) -> JsonResponse:
    """Build a Django ``JsonResponse`` for a validation error response."""
    payload = _validation_error(
        errors=errors,
        message=message,
        code=code,
        status_code=status_code,
        details=details,
        meta=meta,
    )
    return _serialize(payload)


def paginated(
    data: Any = None,
    page: int = 1,
    limit: int = 20,
    total: int = 0,
    message: str | None = None,
    status_code: int = 200,
    meta: Mapping[str, Any] | None = None,
) -> JsonResponse:
    """Build a Django ``JsonResponse`` for a paginated success response."""
    pagination = build_pagination(page=page, limit=limit, total=total)
    payload = _success(
        data=data,
        message=message,
        status_code=status_code,
        meta=meta,
        pagination=pagination,
    )
    return _serialize(payload)


__all__ = [
    "error",
    "paginated",
    "success",
    "validation_error",
]
