"""Tests for Django settings-based configuration reading."""

from __future__ import annotations

import pytest

from api_response_toolkit.config import _build_config, get_config
from django.test import override_settings  # type: ignore[import-not-found]


def test_django_settings_read():
    with override_settings(
        API_RESPONSE_TOOLKIT={
            "DEFAULT_SUCCESS_MESSAGE": "Yay",
            "DEFAULT_ERROR_MESSAGE": "Nope",
            "INCLUDE_META": False,
            "INCLUDE_NULL_DATA": True,
            "DEBUG": True,
            "INCLUDE_TRACEBACK": True,
        }
    ):
        cfg = get_config()
        assert cfg.default_success_message == "Yay"
        assert cfg.default_error_message == "Nope"
        assert cfg.include_meta is False
        assert cfg.include_null_data is True
        assert cfg.debug is True
        assert cfg.include_traceback is True


def test_django_settings_with_extra_keys():
    with override_settings(API_RESPONSE_TOOLKIT={"custom_key": "custom_value"}):
        cfg = get_config()
        assert cfg.extra.get("custom_key") == "custom_value"


def test_django_settings_partial():
    with override_settings(API_RESPONSE_TOOLKIT={"DEFAULT_SUCCESS_MESSAGE": "Hi"}):
        cfg = get_config()
        assert cfg.default_success_message == "Hi"
        # Unspecified keys keep defaults
        assert cfg.default_error_message == "Something went wrong"


def test_django_settings_invalid_type_raises():
    with override_settings(API_RESPONSE_TOOLKIT="not-a-dict"), pytest.raises(TypeError):
        get_config()


def test_build_config_ignores_unknown_and_keeps_extra():
    cfg = _build_config({"default_success_message": "X", "unknown": 1})
    assert cfg.default_success_message == "X"
    assert cfg.extra.get("unknown") == 1


def test_build_config_no_extra_when_all_known():
    cfg = _build_config({"default_success_message": "X"})
    assert cfg.extra == {}


def test_build_config_case_insensitive():
    cfg = _build_config({"DEFAULT_SUCCESS_MESSAGE": "Upper", "DEBUG": True})
    assert cfg.default_success_message == "Upper"
    assert cfg.debug is True
