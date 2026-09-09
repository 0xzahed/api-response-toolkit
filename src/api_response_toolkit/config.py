"""Centralized configuration for the api-response-toolkit package.

The toolkit does not require any configuration for basic usage. When the
optional Django integration is installed, configuration is read from the
``API_RESPONSE_TOOLKIT`` setting in ``settings.py``. For pure-Python usage,
callers may override the global configuration via :func:`configure`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .types import ToolkitConfig

# Module-level mutable configuration holder. This is intentionally a single
# instance; access goes through the functions below to keep the API clean and
# testable.
_config: ToolkitConfig = ToolkitConfig()


def get_config() -> ToolkitConfig:
    """Return the current active configuration.

    When Django is installed and configured, this reads the
    ``API_RESPONSE_TOOLKIT`` setting on every call so that test overrides via
    ``override_settings`` are respected. Otherwise the in-memory configuration
    is returned.
    """
    django_config = _read_django_settings()
    if django_config is not None:
        return _build_config(django_config)
    return _config


def configure(**overrides: Any) -> ToolkitConfig:
    """Update the global (pure-Python) configuration.

    Only the provided keys are overridden; unspecified keys retain their
    current values. Unknown keys are stored in the ``extra`` mapping rather
    than rejected, so callers can attach custom configuration values.

    This has no effect when Django settings are available — in that case,
    configure via ``settings.py`` instead.

    Args:
        **overrides: Configuration keys to override. See :class:`ToolkitConfig`
            for the available keys.

    Returns:
        The newly applied configuration.
    """
    global _config
    current = _config
    known_keys = {
        "default_success_message",
        "default_error_message",
        "include_meta",
        "include_null_data",
        "debug",
        "include_traceback",
    }
    merged = {
        "default_success_message": current.default_success_message,
        "default_error_message": current.default_error_message,
        "include_meta": current.include_meta,
        "include_null_data": current.include_null_data,
        "debug": current.debug,
        "include_traceback": current.include_traceback,
    }
    extra = dict(current.extra)
    for key, value in overrides.items():
        if key in known_keys:
            merged[key] = value
        elif key == "extra" and isinstance(value, Mapping):
            extra.update(value)
        else:
            extra[key] = value
    if extra:
        merged["extra"] = extra
    _config = ToolkitConfig(**merged)  # type: ignore[arg-type]
    return _config


def reset_config() -> None:
    """Reset the global configuration to defaults (useful for tests)."""
    global _config
    _config = ToolkitConfig()


def _build_config(raw: Mapping[str, Any]) -> ToolkitConfig:
    """Build a :class:`ToolkitConfig` from a raw mapping, ignoring unknown keys.

    Keys are matched case-insensitively so both ``"DEFAULT_SUCCESS_MESSAGE"``
    (Django convention) and ``"default_success_message"`` work. Unknown keys
    are preserved in the ``extra`` mapping.
    """
    known = {
        "default_success_message",
        "default_error_message",
        "include_meta",
        "include_null_data",
        "debug",
        "include_traceback",
    }
    kwargs: dict[str, Any] = {}
    extra: dict[str, Any] = {}
    for key, value in raw.items():
        lower = key.lower() if isinstance(key, str) else key
        if lower in known:
            kwargs[lower] = value
        else:
            extra[key] = value
    if extra:
        kwargs["extra"] = extra
    return ToolkitConfig(**kwargs)


def _read_django_settings() -> Mapping[str, Any] | None:
    """Attempt to read the Django ``API_RESPONSE_TOOLKIT`` setting.

    Returns ``None`` if Django is not installed, not configured, or the
    setting is absent.
    """
    try:
        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured
    except ImportError:
        return None

    try:
        configured = getattr(settings, "API_RESPONSE_TOOLKIT", None)
    except ImproperlyConfigured:
        # Settings not configured yet (e.g. during import time).
        return None

    if configured is None:
        return None
    if not isinstance(configured, Mapping):
        raise TypeError(
            "API_RESPONSE_TOOLKIT setting must be a mapping (dict), "
            f"got {type(configured).__name__}"
        )
    return configured


__all__ = ["configure", "get_config", "reset_config"]
