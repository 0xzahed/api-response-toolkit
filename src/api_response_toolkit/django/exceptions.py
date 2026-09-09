"""Django-specific exception handling helpers.

These utilities convert toolkit :class:`APIException` instances (and, when
configured, generic Django/Python exceptions) into standardized JSON
responses. The middleware in :mod:`api_response_toolkit.django.middleware`
uses these helpers.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any, Callable, Optional

from django.conf import settings
from django.http import JsonResponse

from ..config import get_config
from ..exceptions import APIException
from ..response import to_dict
from ..types import ResponsePayload

logger = logging.getLogger("api_response_toolkit")

# Type alias for a custom error handler callable.
ErrorHandler = Callable[[Exception, Mapping[str, Any]], Optional[JsonResponse]]


def build_exception_response(
    exc: Exception,
    *,
    config: Mapping[str, Any] | None = None,
    debug: bool | None = None,
    include_traceback: bool | None = None,
) -> JsonResponse:
    """Build a standardized ``JsonResponse`` for an exception.

    For :class:`APIException` subclasses the structured fields (message, code,
    status_code, errors, details, metadata) are preserved. For unexpected
    exceptions a safe generic 500 response is produced unless debug is enabled.

    Args:
        exc: The exception to convert.
        config: Optional configuration mapping (defaults to the active config).
        debug: Override the debug flag. When ``None``, falls back to the
            config's ``debug`` value or Django's ``DEBUG`` setting.
        include_traceback: Override whether to include tracebacks. When
            ``None``, falls back to the config's ``include_traceback`` value.

    Returns:
        A :class:`django.http.JsonResponse`.
    """
    cfg = get_config()
    if debug is None:
        debug = bool(getattr(cfg, "debug", False)) or bool(getattr(settings, "DEBUG", False))
    if include_traceback is None:
        include_traceback = bool(getattr(cfg, "include_traceback", False))

    if isinstance(exc, APIException):
        payload = ResponsePayload(
            success=False,
            message=exc.message,
            code=exc.code,
            status_code=exc.status_code,
            errors=exc.errors,
            details=exc.details,
            meta=exc.metadata,
        )
        body = to_dict(payload)
        return JsonResponse(
            body,
            status=payload.status_code,
            json_dumps_params={"ensure_ascii": False},
        )

    # Unexpected exception — be safe in production.
    message = "Internal server error"
    if debug:
        message = f"{type(exc).__name__}: {exc}"
    payload = ResponsePayload(
        success=False,
        message=message,
        code="INTERNAL_ERROR",
        status_code=500,
    )
    body = to_dict(payload)
    if debug and include_traceback:
        import traceback

        body["traceback"] = traceback.format_exc()
    return JsonResponse(body, status=500, json_dumps_params={"ensure_ascii": False})


__all__ = ["ErrorHandler", "build_exception_response"]
