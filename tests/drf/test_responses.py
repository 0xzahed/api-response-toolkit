"""Tests for the DRF integration responses."""

from __future__ import annotations

import pytest
from rest_framework.response import Response  # type: ignore[import-not-found]

from api_response_toolkit.drf import (
    error as drf_error,
)
from api_response_toolkit.drf import (
    paginated as drf_paginated,
)
from api_response_toolkit.drf import (
    success as drf_success,
)
from api_response_toolkit.drf import (
    validation_error as drf_validation_error,
)


class TestDRFSuccess:
    def test_returns_response(self):
        resp = drf_success(message="Users fetched successfully", data=[])
        assert isinstance(resp, Response)
        assert resp.status_code == 200
        assert resp.data == {
            "success": True,
            "message": "Users fetched successfully",
            "data": [],
        }

    def test_with_data(self):
        resp = drf_success(data={"id": 1})
        assert resp.data["data"] == {"id": 1}

    def test_with_status_code(self):
        resp = drf_success(message="Created", data={"id": 1}, status_code=201)
        assert resp.status_code == 201

    def test_with_meta(self):
        resp = drf_success(data={}, meta={"request_id": "abc"})
        assert resp.data["meta"] == {"request_id": "abc"}

    def test_invalid_status_code(self):
        with pytest.raises(ValueError):
            drf_success(status_code=404)


class TestDRFError:
    def test_basic(self):
        resp = drf_error(message="User not found", code="USER_NOT_FOUND", status_code=404)
        assert resp.status_code == 404
        assert resp.data == {
            "success": False,
            "message": "User not found",
            "code": "USER_NOT_FOUND",
        }

    def test_with_errors(self):
        resp = drf_error(
            message="Validation failed",
            code="VALIDATION_ERROR",
            status_code=400,
            errors={"email": ["This field is required."]},
        )
        assert resp.data["errors"] == {"email": ["This field is required."]}


class TestDRFValidationError:
    def test_validation_error(self):
        resp = drf_validation_error(
            errors={"email": ["Invalid email address"], "username": ["Username already exists"]}
        )
        assert resp.status_code == 400
        assert resp.data["code"] == "VALIDATION_ERROR"
        assert resp.data["errors"]["email"] == ["Invalid email address"]


class TestDRFPaginated:
    def test_paginated(self):
        resp = drf_paginated(data=[1, 2, 3], page=1, limit=20, total=125)
        assert resp.data["pagination"] == {
            "page": 1,
            "limit": 20,
            "total": 125,
            "total_pages": 7,
        }
        assert resp.data["data"] == [1, 2, 3]
