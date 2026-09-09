"""Tests for the DRF exception handler."""

from __future__ import annotations

import json

from django.test import Client  # type: ignore[import-not-found]
from rest_framework.exceptions import (  # type: ignore[import-not-found]
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
)
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)

from api_response_toolkit import NotFoundError
from api_response_toolkit.drf.exception_handler import api_exception_handler


def _context():
    """Build a minimal DRF context dict for the exception handler."""
    return {"view": None, "request": None, "args": (), "kwargs": {}}


class TestDRFExceptionHandler:
    def test_validation_error(self):
        exc = DRFValidationError({"email": ["Enter a valid email address."]})
        resp = api_exception_handler(exc, _context())
        assert resp is not None
        assert resp.status_code == 400
        assert resp.data == {
            "success": False,
            "message": "Validation failed",
            "code": "VALIDATION_ERROR",
            "errors": {"email": ["Enter a valid email address."]},
        }

    def test_not_found(self):
        exc = NotFound("Not found.")
        resp = api_exception_handler(exc, _context())
        assert resp.status_code == 404
        assert resp.data["code"] == "NOT_FOUND"
        assert resp.data["message"] == "Not found."

    def test_permission_denied(self):
        exc = PermissionDenied("Permission denied.")
        resp = api_exception_handler(exc, _context())
        assert resp.status_code == 403
        assert resp.data["code"] == "FORBIDDEN"

    def test_not_authenticated(self):
        exc = NotAuthenticated()
        resp = api_exception_handler(exc, _context())
        assert resp.status_code == 401
        assert resp.data["code"] == "NOT_AUTHENTICATED"

    def test_authentication_failed(self):
        exc = AuthenticationFailed("Invalid token.")
        resp = api_exception_handler(exc, _context())
        assert resp.status_code == 401
        assert resp.data["code"] == "AUTHENTICATION_FAILED"

    def test_parse_error(self):
        exc = ParseError("Malformed JSON.")
        resp = api_exception_handler(exc, _context())
        assert resp.status_code == 400
        assert resp.data["code"] == "PARSE_ERROR"

    def test_throttled(self):
        exc = Throttled(wait=30)
        resp = api_exception_handler(exc, _context())
        assert resp.status_code == 429
        assert resp.data["code"] == "RATE_LIMITED"
        assert resp.data["details"]["wait"] == 30

    def test_method_not_allowed(self):
        exc = MethodNotAllowed("PUT")
        resp = api_exception_handler(exc, _context())
        assert resp.status_code == 405
        assert resp.data["code"] == "METHOD_NOT_ALLOWED"

    def test_toolkit_api_exception(self):
        exc = NotFoundError(message="User not found", code="USER_NOT_FOUND")
        resp = api_exception_handler(exc, _context())
        assert resp.status_code == 404
        assert resp.data["code"] == "USER_NOT_FOUND"
        assert resp.data["message"] == "User not found"

    def test_unexpected_exception_production(self):
        from django.test import override_settings  # type: ignore[import-not-found]

        with override_settings(DEBUG=False):
            resp = api_exception_handler(RuntimeError("sensitive"), _context())
        assert resp.status_code == 500
        assert resp.data["message"] == "Internal server error"
        assert resp.data["code"] == "INTERNAL_ERROR"
        assert "sensitive" not in json.dumps(resp.data)

    def test_unexpected_exception_debug(self):
        from django.test import override_settings  # type: ignore[import-not-found]

        with override_settings(DEBUG=True):
            resp = api_exception_handler(RuntimeError("debug info"), _context())
        assert resp.status_code == 500
        assert "RuntimeError" in resp.data["message"]


class TestDRFViewIntegration:
    def test_success_view(self):
        client = Client()
        resp = client.get("/drf/success/")
        assert resp.status_code == 200
        body = json.loads(resp.content)
        assert body["success"] is True
        assert body["message"] == "Users fetched successfully"
        assert body["data"] == [{"id": 1}]

    def test_validation_view(self):
        client = Client()
        resp = client.get("/drf/validation/")
        assert resp.status_code == 400
        body = json.loads(resp.content)
        assert body["success"] is False
        assert body["code"] == "VALIDATION_ERROR"
        assert body["errors"]["email"] == ["Enter a valid email address."]

    def test_unhandled_view_production(self):
        from django.test import override_settings  # type: ignore[import-not-found]

        client = Client(raise_request_exception=False)
        with override_settings(DEBUG=False):
            resp = client.get("/drf/unhandled/")
        assert resp.status_code == 500
        body = json.loads(resp.content)
        assert body["message"] == "Internal server error"
        assert body["code"] == "INTERNAL_ERROR"
