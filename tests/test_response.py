"""Tests for the core success/error/validation/paginated response builders."""

from __future__ import annotations

import pytest

from api_response_toolkit import (
    configure,
    error,
    paginated,
    reset_config,
    success,
    to_dict,
    validation_error,
)


class TestSuccessResponse:
    def test_minimal_success(self):
        payload = success()
        body = to_dict(payload)
        assert body == {"success": True, "message": "Success"}
        assert payload.status_code == 200

    def test_success_with_data(self):
        payload = success(data={"id": 1, "name": "Abu"})
        body = to_dict(payload)
        assert body == {
            "success": True,
            "message": "Success",
            "data": {"id": 1, "name": "Abu"},
        }

    def test_success_with_message_and_data(self):
        payload = success(message="User fetched successfully", data={"id": 1})
        body = to_dict(payload)
        assert body["message"] == "User fetched successfully"
        assert body["data"] == {"id": 1}

    def test_success_with_custom_status_code(self):
        payload = success(message="Created", data={"id": 1}, status_code=201)
        assert payload.status_code == 201
        assert to_dict(payload)["success"] is True

    def test_success_with_meta(self):
        payload = success(data={}, meta={"request_id": "abc123", "version": "v1"})
        body = to_dict(payload)
        assert body["meta"] == {"request_id": "abc123", "version": "v1"}

    def test_success_with_pagination(self):
        pagination = {"page": 1, "limit": 20, "total": 125, "total_pages": 7}
        payload = success(data=[], pagination=pagination)
        body = to_dict(payload)
        assert body["pagination"] == pagination

    def test_success_invalid_status_code_rejected(self):
        with pytest.raises(ValueError):
            success(status_code=404)

    def test_success_non_2xx_rejected(self):
        with pytest.raises(ValueError):
            success(status_code=300)

    def test_success_status_code_must_be_int(self):
        with pytest.raises(ValueError):
            success(status_code="200")  # type: ignore[arg-type]

    def test_success_bool_status_code_rejected(self):
        with pytest.raises(ValueError):
            success(status_code=True)  # type: ignore[arg-type]

    def test_success_out_of_range_status_code(self):
        with pytest.raises(ValueError):
            success(status_code=600)

    def test_null_data_omitted_by_default(self):
        body = to_dict(success())
        assert "data" not in body

    def test_include_null_data_config(self):
        configure(include_null_data=True)
        try:
            body = to_dict(success())
            assert body["data"] is None
        finally:
            reset_config()

    def test_meta_omitted_when_config_disabled(self):
        configure(include_meta=False)
        try:
            body = to_dict(success(data={}, meta={"k": "v"}))
            assert "meta" not in body
        finally:
            reset_config()

    def test_default_success_message_config(self):
        configure(default_success_message="Operation completed")
        try:
            body = to_dict(success())
            assert body["message"] == "Operation completed"
        finally:
            reset_config()


class TestErrorResponse:
    def test_minimal_error(self):
        payload = error()
        body = to_dict(payload)
        assert body == {"success": False, "message": "Something went wrong", "code": "BAD_REQUEST"}
        assert payload.status_code == 400

    def test_error_with_code_and_status(self):
        payload = error(message="User not found", code="USER_NOT_FOUND", status_code=404)
        body = to_dict(payload)
        assert body == {
            "success": False,
            "message": "User not found",
            "code": "USER_NOT_FOUND",
        }
        assert payload.status_code == 404

    def test_error_with_errors(self):
        payload = error(
            message="Validation failed",
            code="VALIDATION_ERROR",
            status_code=400,
            errors={
                "email": ["This field is required."],
                "password": ["Password is too short."],
            },
        )
        body = to_dict(payload)
        assert body["errors"]["email"] == ["This field is required."]
        assert body["errors"]["password"] == ["Password is too short."]

    def test_error_with_details(self):
        payload = error(message="Bad request", details={"hint": "check payload"})
        body = to_dict(payload)
        assert body["details"] == {"hint": "check payload"}

    def test_error_with_meta(self):
        payload = error(message="Bad request", meta={"request_id": "abc"})
        body = to_dict(payload)
        assert body["meta"] == {"request_id": "abc"}

    def test_error_with_data(self):
        payload = error(message="Conflict", data={"existing_id": 5}, status_code=409)
        body = to_dict(payload)
        assert body["data"] == {"existing_id": 5}

    def test_error_5xx_allowed(self):
        payload = error(message="Server error", status_code=500)
        assert payload.status_code == 500

    def test_error_invalid_status_code_rejected(self):
        with pytest.raises(ValueError):
            error(status_code=200)

    def test_error_non_4xx_5xx_rejected(self):
        with pytest.raises(ValueError):
            error(status_code=300)

    def test_default_error_message_config(self):
        configure(default_error_message="Oops")
        try:
            body = to_dict(error())
            assert body["message"] == "Oops"
        finally:
            reset_config()


class TestValidationError:
    def test_validation_error_defaults(self):
        payload = validation_error(
            errors={
                "email": ["Invalid email address"],
                "username": ["Username already exists"],
            }
        )
        body = to_dict(payload)
        assert body == {
            "success": False,
            "message": "Validation failed",
            "code": "VALIDATION_ERROR",
            "errors": {
                "email": ["Invalid email address"],
                "username": ["Username already exists"],
            },
        }
        assert payload.status_code == 400

    def test_validation_error_custom_message(self):
        payload = validation_error(errors={"x": ["bad"]}, message="Custom message")
        assert to_dict(payload)["message"] == "Custom message"

    def test_validation_error_custom_status_code(self):
        payload = validation_error(errors={"x": ["bad"]}, status_code=422)
        assert payload.status_code == 422

    def test_validation_error_custom_code(self):
        payload = validation_error(errors={"x": ["bad"]}, code="CUSTOM_CODE")
        assert to_dict(payload)["code"] == "CUSTOM_CODE"


class TestPaginated:
    def test_paginated_basic(self):
        payload = paginated(data=[1, 2, 3], page=1, limit=20, total=125)
        body = to_dict(payload)
        assert body["success"] is True
        assert body["data"] == [1, 2, 3]
        assert body["pagination"] == {
            "page": 1,
            "limit": 20,
            "total": 125,
            "total_pages": 7,
        }

    def test_paginated_total_pages_calculation(self):
        payload = paginated(data=[], page=2, limit=10, total=95)
        assert to_dict(payload)["pagination"]["total_pages"] == 10

    def test_paginated_total_zero(self):
        payload = paginated(data=[], page=1, limit=20, total=0)
        assert to_dict(payload)["pagination"]["total_pages"] == 0

    def test_paginated_limit_zero(self):
        payload = paginated(data=[], page=1, limit=0, total=100)
        assert to_dict(payload)["pagination"]["total_pages"] == 0

    def test_paginated_negative_page_clamped(self):
        payload = paginated(data=[], page=-5, limit=10, total=100)
        assert to_dict(payload)["pagination"]["page"] == 1

    def test_paginated_negative_limit_clamped(self):
        payload = paginated(data=[], page=1, limit=-10, total=100)
        assert to_dict(payload)["pagination"]["limit"] == 0
        assert to_dict(payload)["pagination"]["total_pages"] == 0

    def test_paginated_exact_division(self):
        payload = paginated(data=[], page=1, limit=25, total=100)
        assert to_dict(payload)["pagination"]["total_pages"] == 4

    def test_paginated_large_page(self):
        payload = paginated(data=[], page=9999, limit=20, total=10)
        pagination = to_dict(payload)["pagination"]
        assert pagination["page"] == 9999
        assert pagination["total_pages"] == 1

    def test_paginated_with_message(self):
        payload = paginated(data=[], page=1, limit=10, total=0, message="Users fetched")
        assert to_dict(payload)["message"] == "Users fetched"

    def test_paginated_with_meta(self):
        payload = paginated(data=[], page=1, limit=10, total=0, meta={"k": "v"})
        assert to_dict(payload)["meta"] == {"k": "v"}
