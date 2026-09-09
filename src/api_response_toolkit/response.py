"""Core response builders for the api-response-toolkit package.

This module is framework-agnostic. It produces :class:`ResponsePayload`
instances (and their dictionary representations) that can be serialized to
JSON directly or wrapped by the optional Django/DRF integrations.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from .config import get_config
from .errors import code_for_status
from .types import ErrorMapping, JSONDict, PaginationMeta, ResponsePayload

# ---------------------------------------------------------------------------
# Status code validation
# ---------------------------------------------------------------------------

_SUCCESS_RANGE = (200, 299)
_CLIENT_ERROR_RANGE = (400, 499)
_SERVER_ERROR_RANGE = (500, 599)


def _validate_status_code(status_code: int, *, error: bool) -> int:
    """Validate that ``status_code`` is a plausible HTTP status code.

    Args:
        status_code: The candidate status code.
        error: When ``True`` the code is expected to be an error code
            (4xx/5xx); when ``False`` it is expected to be a success code
            (2xx).

    Returns:
        The validated status code.

    Raises:
        ValueError: If the status code is not a valid HTTP status code or does
            not match the expected category.
    """
    if not isinstance(status_code, int) or isinstance(status_code, bool):
        raise ValueError(f"status_code must be an int, got {type(status_code).__name__}")
    if not 100 <= status_code <= 599:
        raise ValueError(f"status_code must be between 100 and 599, got {status_code}")

    if error:
        if status_code < 400:
            raise ValueError(
                f"error responses require a 4xx/5xx status code, got {status_code}"
            )
    else:
        if not _SUCCESS_RANGE[0] <= status_code <= _SUCCESS_RANGE[1]:
            raise ValueError(
                f"success responses require a 2xx status code, got {status_code}"
            )
    return status_code


# ---------------------------------------------------------------------------
# Pagination helper
# ---------------------------------------------------------------------------

def calculate_total_pages(total: int, limit: int) -> int:
    """Calculate the total number of pages for a paginated collection.

    Handles edge cases:
        * ``total <= 0`` -> ``0`` pages.
        * ``limit <= 0`` -> ``0`` pages (avoids division by zero).
        * Negative inputs are clamped to ``0``.

    Args:
        total: Total number of items.
        limit: Items per page.

    Returns:
        The total number of pages (always ``>= 0``).
    """
    total = max(int(total), 0)
    limit = max(int(limit), 0)
    if total == 0 or limit == 0:
        return 0
    return math.ceil(total / limit)


def build_pagination(
    page: int,
    limit: int,
    total: int,
) -> JSONDict:
    """Build a pagination dictionary with validated, clamped values.

    Negative ``page``/``limit`` are clamped to ``1`` and ``0`` respectively.
    ``total_pages`` is derived via :func:`calculate_total_pages`.

    Args:
        page: Current page number (1-based).
        limit: Number of items per page.
        total: Total number of items.

    Returns:
        A dictionary with ``page``, ``limit``, ``total`` and ``total_pages``.
    """
    page = max(int(page), 1)
    limit = max(int(limit), 0)
    total = max(int(total), 0)
    total_pages = calculate_total_pages(total, limit)
    return PaginationMeta(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
    ).to_dict()


# ---------------------------------------------------------------------------
# Success / error / validation / paginated builders
# ---------------------------------------------------------------------------

def success(
    data: Any = None,
    message: str | None = None,
    status_code: int = 200,
    meta: Mapping[str, Any] | None = None,
    pagination: Mapping[str, Any] | None = None,
) -> ResponsePayload:
    """Build a success response payload.

    Args:
        data: The response data (any JSON-serializable value).
        message: Human-readable success message. Defaults to the configured
            ``default_success_message``.
        status_code: HTTP status code (must be 2xx).
        meta: Optional metadata mapping.
        pagination: Optional pagination mapping.

    Returns:
        A :class:`ResponsePayload` with ``success=True``.

    Raises:
        ValueError: If ``status_code`` is not a valid 2xx code.
    """
    config = get_config()
    _validate_status_code(status_code, error=False)
    return ResponsePayload(
        success=True,
        message=message if message is not None else config.default_success_message,
        data=data,
        meta=dict(meta) if meta is not None else None,
        pagination=dict(pagination) if pagination is not None else None,
        status_code=status_code,
    )


def error(
    message: str | None = None,
    code: str | None = None,
    status_code: int = 400,
    data: Any = None,
    errors: ErrorMapping | None = None,
    details: Any = None,
    meta: Mapping[str, Any] | None = None,
) -> ResponsePayload:
    """Build an error response payload.

    Args:
        message: Human-readable error message. Defaults to the configured
            ``default_error_message``.
        code: Optional machine-readable error code (e.g. ``"USER_NOT_FOUND"``).
        status_code: HTTP status code (must be 4xx or 5xx).
        data: Optional data payload (rarely used for errors).
        errors: Optional mapping of field errors.
        details: Optional extra error details.
        meta: Optional metadata mapping.

    Returns:
        A :class:`ResponsePayload` with ``success=False``.

    Raises:
        ValueError: If ``status_code`` is not a valid 4xx/5xx code.
    """
    config = get_config()
    _validate_status_code(status_code, error=True)
    resolved_code = code if code is not None else code_for_status(status_code)
    return ResponsePayload(
        success=False,
        message=message if message is not None else config.default_error_message,
        data=data,
        code=resolved_code,
        errors=dict(errors) if errors is not None else None,
        details=details,
        meta=dict(meta) if meta is not None else None,
        status_code=status_code,
    )


def validation_error(
    errors: ErrorMapping,
    message: str = "Validation failed",
    code: str = "VALIDATION_ERROR",
    status_code: int = 400,
    details: Any = None,
    meta: Mapping[str, Any] | None = None,
) -> ResponsePayload:
    """Build a validation error response payload.

    Args:
        errors: Mapping of field names to error messages/lists.
        message: Human-readable message. Defaults to ``"Validation failed"``.
        code: Machine-readable code. Defaults to ``"VALIDATION_ERROR"``.
        status_code: HTTP status code (must be 4xx/5xx). Defaults to ``400``.
        details: Optional extra error details.
        meta: Optional metadata mapping.

    Returns:
        A :class:`ResponsePayload` with ``success=False``.

    Raises:
        ValueError: If ``status_code`` is not a valid 4xx/5xx code.
    """
    return error(
        message=message,
        code=code,
        status_code=status_code,
        errors=errors,
        details=details,
        meta=meta,
    )


def paginated(
    data: Any = None,
    page: int = 1,
    limit: int = 20,
    total: int = 0,
    message: str | None = None,
    status_code: int = 200,
    meta: Mapping[str, Any] | None = None,
) -> ResponsePayload:
    """Build a paginated success response payload.

    The pagination metadata (including ``total_pages``) is computed
    automatically from ``page``, ``limit`` and ``total``.

    Args:
        data: The slice of items for the current page.
        page: Current page number (1-based; negative values are clamped to 1).
        limit: Items per page (negative values are clamped to 0).
        total: Total number of items across all pages.
        message: Optional success message.
        status_code: HTTP status code (must be 2xx).
        meta: Optional metadata mapping.

    Returns:
        A :class:`ResponsePayload` with ``success=True`` and a
        ``pagination`` field.
    """
    pagination = build_pagination(page=page, limit=limit, total=total)
    return success(
        data=data,
        message=message,
        status_code=status_code,
        meta=meta,
        pagination=pagination,
    )


def to_dict(payload: ResponsePayload) -> JSONDict:
    """Serialize a :class:`ResponsePayload` using the active configuration."""
    config = get_config()
    return payload.to_dict(
        include_null_data=config.include_null_data,
        include_meta=config.include_meta,
    )


__all__ = [
    "build_pagination",
    "calculate_total_pages",
    "error",
    "paginated",
    "success",
    "to_dict",
    "validation_error",
]
