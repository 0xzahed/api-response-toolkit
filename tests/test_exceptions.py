"""Tests for the custom exception classes."""

from __future__ import annotations

import pytest

from api_response_toolkit import (
    APIException,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
    from_status_code,
)


class TestAPIException:
    def test_defaults(self):
        exc = APIException()
        assert exc.message == "An error occurred."
        assert exc.code == "API_ERROR"
        assert exc.status_code == 500
        assert exc.errors is None
        assert exc.details is None
        assert exc.metadata is None

    def test_custom_fields(self):
        exc = APIException(
            message="Custom",
            code="CUSTOM",
            status_code=400,
            errors={"field": ["bad"]},
            details={"hint": "x"},
            metadata={"request_id": "r1"},
        )
        assert exc.message == "Custom"
        assert exc.code == "CUSTOM"
        assert exc.status_code == 400
        assert exc.errors == {"field": ["bad"]}
        assert exc.details == {"hint": "x"}
        assert exc.metadata == {"request_id": "r1"}

    def test_to_payload(self):
        exc = APIException(message="m", code="c", status_code=400, errors={"f": ["e"]})
        payload = exc.to_payload()
        assert payload == {
            "success": False,
            "message": "m",
            "code": "c",
            "errors": {"f": ["e"]},
        }

    def test_to_payload_with_details_and_meta(self):
        exc = APIException(
            message="m", code="c", status_code=400, details="d", metadata={"k": "v"}
        )
        payload = exc.to_payload()
        assert payload["details"] == "d"
        assert payload["meta"] == {"k": "v"}

    def test_is_exception_subclass(self):
        assert issubclass(NotFoundError, APIException)
        assert issubclass(APIException, Exception)

    def test_str_representation(self):
        exc = APIException(message="boom")
        assert str(exc) == "boom"


class TestSpecificExceptions:
    @pytest.mark.parametrize(
        "exc_cls, expected_status, expected_code",
        [
            (NotFoundError, 404, "NOT_FOUND"),
            (UnauthorizedError, 401, "UNAUTHORIZED"),
            (ForbiddenError, 403, "FORBIDDEN"),
            (ValidationError, 400, "VALIDATION_ERROR"),
            (BadRequestError, 400, "BAD_REQUEST"),
            (ConflictError, 409, "CONFLICT"),
            (InternalServerError, 500, "INTERNAL_ERROR"),
        ],
    )
    def test_defaults(self, exc_cls, expected_status, expected_code):
        exc = exc_cls()
        assert exc.status_code == expected_status
        assert exc.code == expected_code

    def test_not_found_custom(self):
        exc = NotFoundError(message="User not found", code="USER_NOT_FOUND")
        assert exc.message == "User not found"
        assert exc.code == "USER_NOT_FOUND"
        assert exc.status_code == 404

    def test_validation_error_with_errors(self):
        exc = ValidationError(errors={"email": ["Invalid"]})
        assert exc.errors == {"email": ["Invalid"]}
        assert exc.status_code == 400

    def test_raise_and_catch(self):
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError(message="User not found", code="USER_NOT_FOUND")
        assert exc_info.value.code == "USER_NOT_FOUND"


class TestFromStatusCode:
    def test_404_maps_to_not_found(self):
        exc = from_status_code(404, message="Not found")
        assert isinstance(exc, NotFoundError)
        assert exc.status_code == 404
        assert exc.code == "NOT_FOUND"

    def test_401_maps_to_unauthorized(self):
        exc = from_status_code(401)
        assert isinstance(exc, UnauthorizedError)

    def test_403_maps_to_forbidden(self):
        exc = from_status_code(403)
        assert isinstance(exc, ForbiddenError)

    def test_409_maps_to_conflict(self):
        exc = from_status_code(409)
        assert isinstance(exc, ConflictError)

    def test_500_maps_to_internal(self):
        exc = from_status_code(500)
        assert isinstance(exc, InternalServerError)

    def test_400_maps_to_bad_request(self):
        exc = from_status_code(400)
        assert isinstance(exc, BadRequestError)

    def test_unknown_status_falls_back_to_base(self):
        exc = from_status_code(418)
        assert isinstance(exc, APIException)
        assert exc.code == "BAD_REQUEST"

    def test_unknown_5xx_falls_back(self):
        exc = from_status_code(599)
        assert isinstance(exc, APIException)
        assert exc.code == "INTERNAL_ERROR"

    def test_with_errors_and_details(self):
        exc = from_status_code(400, errors={"x": ["bad"]}, details="d")
        assert exc.errors == {"x": ["bad"]}
        assert exc.details == "d"
