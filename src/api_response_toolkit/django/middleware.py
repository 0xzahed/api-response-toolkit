"""Optional Django middleware for handling unhandled API exceptions.

The middleware catches :class:`api_response_toolkit.APIException` instances
raised during request processing and converts them to standardized JSON
responses. For unexpected exceptions it returns a safe generic 500 response
(never exposing stack traces when ``DEBUG=False``).

Configuration (via ``settings.API_RESPONSE_TOOLKIT``):

    API_RESPONSE_TOOLKIT = {
        "middleware_enabled": True,        # enable/disable the middleware
        "middleware_debug": False,          # override debug behavior
        "include_traceback": False,         # include tracebacks when debug
        "custom_error_handler": None,     # dotted path to a callable
    }

The middleware only intervenes for requests that look like API requests
(content type ``application/json`` or path starting with ``/api/`` by
default), unless ``middleware_enabled`` forces it for all requests. This
ensures Django's normal HTML debug/error pages are preserved for non-API
requests.
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from typing import Any, Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from ..exceptions import APIException
from .exceptions import build_exception_response

_DEFAULT_API_PREFIX = "/api/"
_DEFAULT_API_CONTENT_TYPE = "application/json"


def _get_middleware_config() -> Mapping[str, Any]:
    """Read middleware-specific options from the Django settings mapping."""
    configured = getattr(settings, "API_RESPONSE_TOOLKIT", None)
    if not isinstance(configured, Mapping):
        return {}
    return configured


def _is_api_request(request: HttpRequest) -> bool:
    """Heuristic: does this request look like an API request?"""
    path = getattr(request, "path", "") or ""
    if path.startswith(_DEFAULT_API_PREFIX):
        return True
    accept = (request.META.get("HTTP_ACCEPT", "") or "").lower()
    content_type = (request.META.get("CONTENT_TYPE", "") or "").lower()
    return _DEFAULT_API_CONTENT_TYPE in accept or _DEFAULT_API_CONTENT_TYPE in content_type


def _load_custom_handler(dotted_path: str) -> Callable[..., JsonResponse | None]:
    """Import a callable from a dotted path."""
    module_path, _, attr = dotted_path.rpartition(".")
    if not module_path:
        raise ValueError(f"Invalid custom_error_handler path: {dotted_path!r}")
    module = importlib.import_module(module_path)
    handler: Any = getattr(module, attr)
    if not callable(handler):
        raise TypeError(f"custom_error_handler {dotted_path!r} is not callable")
    return handler  # type: ignore[no-any-return]


class APIExceptionMiddleware:
    """Middleware that converts exceptions into standardized API responses."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        try:
            return self.get_response(request)
        except Exception as exc:  # noqa: BLE001 - intentional broad catch
            result = self.process_exception(request, exc)
            if result is not None:
                return result
            raise

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> HttpResponse | None:
        """Handle an exception raised during request processing.

        Returns a ``JsonResponse`` for API requests, or ``None`` to defer to
        Django's default handling for non-API requests.
        """
        mw_config = _get_middleware_config()

        # Allow disabling the middleware entirely.
        if mw_config.get("middleware_enabled", True) is False:
            return None

        # Only intervene for API requests (unless it's our own APIException,
        # which is always safe to convert).
        if not isinstance(exception, APIException) and not _is_api_request(request):
            return None

        # Allow a custom error handler to take over.
        custom_path = mw_config.get("custom_error_handler")
        if custom_path:
            handler = _load_custom_handler(str(custom_path))
            result = handler(exception, mw_config)
            if result is not None:
                return result

        # Resolve debug/traceback overrides from middleware config.
        debug_override = mw_config.get("middleware_debug")
        if debug_override is None:
            debug_override = None
        include_traceback = mw_config.get("include_traceback")

        return build_exception_response(
            exception,
            debug=bool(debug_override) if debug_override is not None else None,
            include_traceback=bool(include_traceback) if include_traceback is not None else None,
        )


__all__ = ["APIExceptionMiddleware"]
