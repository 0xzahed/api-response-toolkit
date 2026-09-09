"""Custom DRF exception handler producing standardized API responses.

Configure it in your ``settings.py``::

    REST_FRAMEWORK = {
        "EXCEPTION_HANDLER":
            "api_response_toolkit.drf.exception_handler.api_exception_handler"
    }

The handler normalizes DRF's built-in exceptions (and Django exceptions where
appropriate) into the toolkit's response envelope while preserving DRF's
existing behavior for non-API contexts.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from django.conf import settings
from django.core.exceptions import (
    PermissionDenied as DjangoPermissionDenied,
)
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import (
    exception_handler as drf_default_handler,
)

from ..config import get_config
from ..exceptions import APIException
from ..types import JSONDict

logger = logging.getLogger("api_response_toolkit")


def _flatten_errors(detail: Any) -> Any:
    """Convert DRF's ``ErrorDetail`` objects into plain strings/lists.

    DRF represents field errors as nested structures of ``ErrorDetail``
    instances. This helper recursively converts them to plain strings and
    lists so the output is JSON-serializable and predictable.
    """
    # ErrorDetail is a str subclass with a `code` attribute.
    if isinstance(detail, str) and not isinstance(detail, (list, dict)):
        return str(detail)
    if isinstance(detail, list):
        return [_flatten_errors(item) for item in detail]
    if isinstance(detail, dict):
        return {str(key): _flatten_errors(value) for key, value in detail.items()}
    return str(detail)


def _errors_to_dict(detail: Any) -> JSONDict:
    """Normalize DRF error detail into a field->messages mapping."""
    flattened = _flatten_errors(detail)
    if isinstance(flattened, dict):
        return flattened
    if isinstance(flattened, str):
        return {"non_field_errors": [flattened]}
    if isinstance(flattened, list):
        return {"non_field_errors": flattened}
    return {"non_field_errors": [str(flattened)]}


def _build_response(
    *,
    message: str,
    code: str,
    status_code: int,
    errors: JSONDict | None = None,
    details: Any = None,
    meta: JSONDict | None = None,
) -> Response:
    """Construct a standardized DRF ``Response``."""
    body: JSONDict = {
        "success": False,
        "message": message,
        "code": code,
    }
    if errors is not None:
        body["errors"] = errors
    if details is not None:
        body["details"] = details
    if meta is not None:
        body["meta"] = meta
    return Response(body, status=status_code)


def _handle_drf_exception(exc: Exception) -> Response | None:
    """Map a DRF/Django exception to a standardized response.

    Returns ``None`` for exception types this handler does not own.
    """
    config = get_config()

    # --- Toolkit's own APIException ----------------------------------------
    if isinstance(exc, APIException):
        return _build_response(
            message=exc.message,
            code=exc.code,
            status_code=exc.status_code,
            errors=exc.errors,
            details=exc.details,
            meta=exc.metadata,
        )

    # --- DRF ValidationError ------------------------------------------------
    if isinstance(exc, drf_exceptions.ValidationError):
        return _build_response(
            message="Validation failed",
            code="VALIDATION_ERROR",
            status_code=exc.status_code,
            errors=_errors_to_dict(exc.detail),
        )

    # --- DRF NotFound -------------------------------------------------------
    if isinstance(exc, drf_exceptions.NotFound):
        message = str(exc.detail) if exc.detail else "Not found."
        return _build_response(
            message=message,
            code="NOT_FOUND",
            status_code=exc.status_code,
        )

    # --- Django Http404 -----------------------------------------------------
    if isinstance(exc, Http404):
        message = str(exc) or "Not found."
        return _build_response(
            message=message,
            code="NOT_FOUND",
            status_code=404,
        )

    # --- DRF PermissionDenied -----------------------------------------------
    if isinstance(exc, drf_exceptions.PermissionDenied):
        message = str(exc.detail) if exc.detail else "Permission denied."
        return _build_response(
            message=message,
            code="FORBIDDEN",
            status_code=exc.status_code,
        )

    # --- Django PermissionDenied --------------------------------------------
    if isinstance(exc, DjangoPermissionDenied):
        return _build_response(
            message=str(exc) or "Permission denied.",
            code="FORBIDDEN",
            status_code=403,
        )

    # --- DRF NotAuthenticated -----------------------------------------------
    if isinstance(exc, drf_exceptions.NotAuthenticated):
        message = str(exc.detail) if exc.detail else "Authentication credentials were not provided."
        return _build_response(
            message=message,
            code="NOT_AUTHENTICATED",
            status_code=exc.status_code,
        )

    # --- DRF AuthenticationFailed -------------------------------------------
    if isinstance(exc, drf_exceptions.AuthenticationFailed):
        message = str(exc.detail) if exc.detail else "Authentication failed."
        return _build_response(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=exc.status_code,
        )

    # --- DRF ParseError -----------------------------------------------------
    if isinstance(exc, drf_exceptions.ParseError):
        message = str(exc.detail) if exc.detail else "Malformed request."
        return _build_response(
            message=message,
            code="PARSE_ERROR",
            status_code=exc.status_code,
        )

    # --- DRF Throttled ------------------------------------------------------
    if isinstance(exc, drf_exceptions.Throttled):
        message = str(exc.detail) if exc.detail else "Request was throttled."
        details: JSONDict = {}
        if getattr(exc, "wait", None) is not None:
            details["wait"] = exc.wait
        return _build_response(
            message=message,
            code="RATE_LIMITED",
            status_code=exc.status_code,
            details=details or None,
        )

    # --- DRF MethodNotAllowed -----------------------------------------------
    if isinstance(exc, drf_exceptions.MethodNotAllowed):
        message = str(exc.detail) if exc.detail else "Method not allowed."
        return _build_response(
            message=message,
            code="METHOD_NOT_ALLOWED",
            status_code=exc.status_code,
        )

    # --- DRF UnsupportedMediaType -------------------------------------------
    if isinstance(exc, drf_exceptions.UnsupportedMediaType):
        message = str(exc.detail) if exc.detail else "Unsupported media type."
        return _build_response(
            message=message,
            code="UNSUPPORTED_MEDIA_TYPE",
            status_code=exc.status_code,
        )

    # --- Generic DRF APIException (not matched above) -----------------------
    if isinstance(exc, drf_exceptions.APIException):
        message = str(exc.detail) if exc.detail else config.default_error_message
        code = getattr(exc.detail, "code", None) or "API_ERROR"
        errors = _errors_to_dict(exc.detail) if exc.detail else None
        return _build_response(
            message=message,
            code=str(code).upper() if isinstance(code, str) else "API_ERROR",
            status_code=exc.status_code,
            errors=errors,
        )

    return None


def api_exception_handler(exc: Exception, context: Mapping[str, Any]) -> Response | None:
    """Standardized DRF exception handler.

    This first delegates to DRF's default handler to determine whether the
    exception should be handled (DRF returns ``None`` for exceptions it does
    not recognize, e.g. generic ``Http404``/``PermissionDenied``). If DRF
    would handle it, we produce our standardized envelope instead.

    For unexpected exceptions, a safe generic 500 response is returned when
    ``DEBUG=False``; when ``DEBUG=True`` the exception type and message are
    included for easier debugging.
    """
    # Let DRF decide if this exception is in scope. We still want to handle
    # our own APIException and Django-level exceptions even if DRF returns
    # None, so we check those explicitly afterward.
    drf_response = drf_default_handler(exc, context)

    standardized = _handle_drf_exception(exc)
    if standardized is not None:
        return standardized

    # If DRF handled it but we didn't (shouldn't normally happen for known
    # types), fall back to DRF's response.
    if drf_response is not None:
        return drf_response

    # Unexpected exception — be safe in production.
    debug = bool(getattr(settings, "DEBUG", False)) or get_config().debug
    message = f"{type(exc).__name__}: {exc}" if debug else "Internal server error"
    logger.exception("Unhandled exception in DRF view")
    return _build_response(
        message=message,
        code="INTERNAL_ERROR",
        status_code=500,
    )


__all__ = ["api_exception_handler"]
