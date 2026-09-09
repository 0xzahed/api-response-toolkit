"""Tests for the Django middleware."""

from __future__ import annotations

import json

from django.test import Client, override_settings  # type: ignore[import-not-found]


def _client():
    """A test client that does not re-raise unhandled exceptions."""
    return Client(raise_request_exception=False)


def test_api_exception_converted():
    client = _client()
    resp = client.get("/plain/unhandled/")
    assert resp.status_code == 404
    body = json.loads(resp.content)
    assert body["success"] is False
    assert body["code"] == "USER_NOT_FOUND"


@override_settings(API_RESPONSE_TOOLKIT={"middleware_enabled": False})
def test_middleware_disabled():
    # When disabled, the exception propagates to Django's default handler,
    # which returns a 500 for a non-Http404 exception.
    client = _client()
    resp = client.get("/plain/unhandled/")
    assert resp.status_code == 500


def test_non_api_request_success():
    client = _client()
    resp = client.get("/plain/success/")
    assert resp.status_code == 200


def test_debug_includes_message():
    from api_response_toolkit.django.exceptions import build_exception_response

    resp = build_exception_response(ValueError("boom"), debug=True)
    body = json.loads(resp.content)
    assert resp.status_code == 500
    assert "ValueError" in body["message"]


def test_debug_with_traceback():
    from api_response_toolkit.django.exceptions import build_exception_response

    try:
        raise ValueError("boom")
    except ValueError as exc:
        resp = build_exception_response(exc, debug=True, include_traceback=True)
    body = json.loads(resp.content)
    assert resp.status_code == 500
    assert "traceback" in body
    assert "ValueError" in body["traceback"]


def test_production_hides_details():
    from api_response_toolkit.django.exceptions import build_exception_response

    resp = build_exception_response(ValueError("sensitive info"), debug=False)
    body = json.loads(resp.content)
    assert resp.status_code == 500
    assert body["message"] == "Internal server error"
    assert "sensitive" not in json.dumps(body)


def test_api_exception_preserves_fields():
    from api_response_toolkit import NotFoundError
    from api_response_toolkit.django.exceptions import build_exception_response

    exc = NotFoundError(
        message="User not found",
        code="USER_NOT_FOUND",
        errors={"id": ["missing"]},
        details="hint",
        metadata={"request_id": "r1"},
    )
    resp = build_exception_response(exc)
    body = json.loads(resp.content)
    assert resp.status_code == 404
    assert body["message"] == "User not found"
    assert body["code"] == "USER_NOT_FOUND"
    assert body["errors"] == {"id": ["missing"]}
    assert body["details"] == "hint"
    assert body["meta"] == {"request_id": "r1"}
