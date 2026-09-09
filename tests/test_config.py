"""Tests for the configuration system."""

from __future__ import annotations

from api_response_toolkit import configure, get_config, reset_config


def test_default_config():
    reset_config()
    cfg = get_config()
    assert cfg.default_success_message == "Success"
    assert cfg.default_error_message == "Something went wrong"
    assert cfg.include_meta is True
    assert cfg.include_null_data is False
    assert cfg.debug is False
    assert cfg.include_traceback is False


def test_configure_partial_override():
    reset_config()
    configure(default_success_message="Done")
    cfg = get_config()
    assert cfg.default_success_message == "Done"
    # Other keys unchanged
    assert cfg.default_error_message == "Something went wrong"


def test_configure_multiple_keys():
    reset_config()
    configure(include_null_data=True, debug=True)
    cfg = get_config()
    assert cfg.include_null_data is True
    assert cfg.debug is True


def test_reset_config():
    configure(default_success_message="Temp")
    reset_config()
    cfg = get_config()
    assert cfg.default_success_message == "Success"


def test_extra_keys_preserved():
    reset_config()
    configure(custom_key="value")  # type: ignore[call-arg]
    cfg = get_config()
    assert cfg.extra.get("custom_key") == "value"


def test_config_is_immutable_instance():
    reset_config()
    cfg1 = get_config()
    configure(default_success_message="Changed")
    cfg2 = get_config()
    # The previous instance is not mutated
    assert cfg1.default_success_message == "Success"
    assert cfg2.default_success_message == "Changed"
