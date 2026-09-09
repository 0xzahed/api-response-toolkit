"""Tests for the Django integration responses."""

from __future__ import annotations

import json

import pytest

from api_response_toolkit.django import (
    error as django_error,
)
from api_response_toolkit.django import (
    paginated as django_paginated,
)
from api_response_toolkit.django import (
    success as django_success,
)
from api_response_toolkit.django import (
    validation_error as django_validation_error,
)


def _body(response):
    return json.loads(response.content)


class TestDjangoSuccess:
    def test_returns_json_response(self):
        resp = django_success(message="Users fetched successfully", data=[])
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/json"
        assert _body(resp) == {
            "success": True,
            "message": "Users fetched successfully",
            "data": [],
        }

    def test_with_data_dict(self):
        resp = django_success(data={"id": 1, "name": "Abu"})
        assert _body(resp)["data"] == {"id": 1, "name": "Abu"}

    def test_with_status_code(self):
        resp = django_success(message="Created", data={"id": 1}, status_code=201)
        assert resp.status_code == 201

    def test_with_meta(self):
        resp = django_success(data={}, meta={"request_id": "abc"})
        assert _body(resp)["meta"] == {"request_id": "abc"}

    def test_invalid_status_code_raises(self):
        with pytest.raises(ValueError):
            django_success(status_code=404)


class TestDjangoError:
    def test_basic_error(self):
        resp = django_error(message="User not found", code="USER_NOT_FOUND", status_code=404)
        assert resp.status_code == 404
        assert _body(resp) == {
            "success": False,
            "message": "User not found",
            "code": "USER_NOT_FOUND",
        }

    def test_with_errors(self):
        resp = django_error(
            message="Validation failed",
            code="VALIDATION_ERROR",
            status_code=400,
            errors={"email": ["This field is required."]},
        )
        assert _body(resp)["errors"] == {"email": ["This field is required."]}


class TestDjangoValidationError:
    def test_validation_error(self):
        resp = django_validation_error(
            errors={"email": ["Invalid email address"], "username": ["Username already exists"]}
        )
        body = _body(resp)
        assert resp.status_code == 400
        assert body["success"] is False
        assert body["code"] == "VALIDATION_ERROR"
        assert body["errors"]["email"] == ["Invalid email address"]


class TestDjangoPaginated:
    def test_paginated(self):
        resp = django_paginated(data=[1, 2, 3], page=1, limit=20, total=125)
        body = _body(resp)
        assert body["pagination"] == {
            "page": 1,
            "limit": 20,
            "total": 125,
            "total_pages": 7,
        }
        assert body["data"] == [1, 2, 3]


class TestDjangoViewIntegration:
    def test_plain_django_view(self):
        from django.test import Client  # type: ignore[import-not-found]

        client = Client()
        resp = client.get("/plain/success/")
        assert resp.status_code == 200
        body = json.loads(resp.content)
        assert body["success"] is True
        assert body["message"] == "Users fetched successfully"
        assert body["data"] == [{"id": 1}]

    def test_plain_django_view_unhandled_api_exception(self):
        from django.test import Client  # type: ignore[import-not-found]

        client = Client(raise_request_exception=False)
        resp = client.get("/plain/unhandled/")
        # NotFoundError raised -> middleware converts to 404 JSON
        assert resp.status_code == 404
        body = json.loads(resp.content)
        assert body["success"] is False
        assert body["message"] == "User not found"
        assert body["code"] == "USER_NOT_FOUND"
