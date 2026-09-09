"""Tests for less common DRF exception handler paths."""

from __future__ import annotations

from django.core.exceptions import (
    PermissionDenied as DjangoPermissionDenied,  # type: ignore[import-not-found]
)
from django.http import Http404  # type: ignore[import-not-found]
from rest_framework.exceptions import (  # type: ignore[import-not-found]
    APIException as DRFAPIException,
)
from rest_framework.exceptions import (
    ErrorDetail,
    UnsupportedMediaType,
)

from api_response_toolkit.drf.exception_handler import (
    _errors_to_dict,
    _flatten_errors,
    api_exception_handler,
)


def _context():
    return {"view": None, "request": None, "args": (), "kwargs": {}}


def test_flatten_errors_string():
    assert _flatten_errors("hello") == "hello"


def test_flatten_errors_error_detail():
    detail = ErrorDetail("bad value", code="invalid")
    assert _flatten_errors(detail) == "bad value"


def test_flatten_errors_list():
    assert _flatten_errors(["a", "b"]) == ["a", "b"]


def test_flatten_errors_dict():
    assert _flatten_errors({"k": ["v"]}) == {"k": ["v"]}


def test_flatten_errors_other():
    assert _flatten_errors(123) == "123"


def test_errors_to_dict_string():
    result = _errors_to_dict("a plain string")
    assert result == {"non_field_errors": ["a plain string"]}


def test_errors_to_dict_list():
    result = _errors_to_dict(["a", "b"])
    assert result == {"non_field_errors": ["a", "b"]}


def test_errors_to_dict_dict():
    result = _errors_to_dict({"email": ["bad"]})
    assert result == {"email": ["bad"]}


def test_django_http404():
    exc = Http404("No such thing")
    resp = api_exception_handler(exc, _context())
    assert resp.status_code == 404
    assert resp.data["code"] == "NOT_FOUND"
    assert "No such thing" in resp.data["message"]


def test_django_permission_denied():
    exc = DjangoPermissionDenied("nope")
    resp = api_exception_handler(exc, _context())
    assert resp.status_code == 403
    assert resp.data["code"] == "FORBIDDEN"


def test_unsupported_media_type():
    exc = UnsupportedMediaType("application/xml")
    resp = api_exception_handler(exc, _context())
    assert resp.status_code == 415
    assert resp.data["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_generic_drf_api_exception():
    exc = DRFAPIException(detail="something broke", code="broken")
    resp = api_exception_handler(exc, _context())
    assert resp.status_code == 500
    assert resp.data["code"] == "BROKEN"


def test_generic_drf_api_exception_with_string_detail():
    exc = DRFAPIException(detail="custom message")
    resp = api_exception_handler(exc, _context())
    assert resp.data["message"] == "custom message"


def test_drf_not_found_with_empty_detail():
    from rest_framework.exceptions import NotFound  # type: ignore[import-not-found]

    exc = NotFound()
    resp = api_exception_handler(exc, _context())
    assert resp.status_code == 404
    assert resp.data["code"] == "NOT_FOUND"


def test_drf_permission_denied_with_empty_detail():
    from rest_framework.exceptions import PermissionDenied  # type: ignore[import-not-found]

    exc = PermissionDenied()
    resp = api_exception_handler(exc, _context())
    assert resp.status_code == 403
    assert resp.data["code"] == "FORBIDDEN"


def test_drf_throttled_no_wait():
    from rest_framework.exceptions import Throttled  # type: ignore[import-not-found]

    exc = Throttled()
    resp = api_exception_handler(exc, _context())
    assert resp.status_code == 429
    assert resp.data["code"] == "RATE_LIMITED"
    assert "details" not in resp.data
