"""Tests for the error code constants and helpers."""

from __future__ import annotations

from api_response_toolkit import errors as errors_module
from api_response_toolkit.errors import (
    BAD_REQUEST,
    CONFLICT,
    FORBIDDEN,
    INTERNAL_ERROR,
    NOT_FOUND,
    RATE_LIMITED,
    SERVICE_UNAVAILABLE,
    STATUS_CODE_TO_CODE,
    TIMEOUT,
    UNAUTHORIZED,
    VALIDATION_ERROR,
    code_for_status,
)


def test_constants_exist():
    assert VALIDATION_ERROR == "VALIDATION_ERROR"
    assert NOT_FOUND == "NOT_FOUND"
    assert UNAUTHORIZED == "UNAUTHORIZED"
    assert FORBIDDEN == "FORBIDDEN"
    assert BAD_REQUEST == "BAD_REQUEST"
    assert CONFLICT == "CONFLICT"
    assert INTERNAL_ERROR == "INTERNAL_ERROR"
    assert RATE_LIMITED == "RATE_LIMITED"
    assert TIMEOUT == "TIMEOUT"
    assert SERVICE_UNAVAILABLE == "SERVICE_UNAVAILABLE"


def test_status_code_to_code_mapping():
    assert STATUS_CODE_TO_CODE[404] == NOT_FOUND
    assert STATUS_CODE_TO_CODE[401] == UNAUTHORIZED
    assert STATUS_CODE_TO_CODE[403] == FORBIDDEN
    assert STATUS_CODE_TO_CODE[400] == BAD_REQUEST
    assert STATUS_CODE_TO_CODE[409] == CONFLICT
    assert STATUS_CODE_TO_CODE[500] == INTERNAL_ERROR
    assert STATUS_CODE_TO_CODE[429] == RATE_LIMITED
    assert STATUS_CODE_TO_CODE[503] == SERVICE_UNAVAILABLE


def test_code_for_status_known():
    assert code_for_status(404) == NOT_FOUND
    assert code_for_status(500) == INTERNAL_ERROR


def test_code_for_status_unknown_5xx():
    assert code_for_status(599) == INTERNAL_ERROR


def test_code_for_status_unknown_4xx():
    assert code_for_status(418) == BAD_REQUEST


def test_code_for_status_unknown_3xx_falls_back():
    # Below 400 and not in mapping -> BAD_REQUEST fallback
    assert code_for_status(302) == BAD_REQUEST


def test_all_codes_exported_in_module():
    expected = {
        "VALIDATION_ERROR",
        "NOT_FOUND",
        "UNAUTHORIZED",
        "FORBIDDEN",
        "BAD_REQUEST",
        "CONFLICT",
        "INTERNAL_ERROR",
        "NOT_IMPLEMENTED",
        "SERVICE_UNAVAILABLE",
        "RATE_LIMITED",
        "TIMEOUT",
        "PARSE_ERROR",
        "METHOD_NOT_ALLOWED",
        "UNSUPPORTED_MEDIA_TYPE",
    }
    assert expected.issubset(set(errors_module.__all__))
