"""Django app configuration for api-response-toolkit.

This app config exists primarily so that the package can be listed in
``INSTALLED_APPS`` (useful for the middleware and for autodiscovery). It does
not install any models or require database tables.
"""

from __future__ import annotations

try:
    from django.apps import AppConfig
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "api_response_toolkit.django requires Django to be installed. "
        'Install it with: pip install "api-response-toolkit[django]"'
    ) from exc


class ApiResponseToolkitConfig(AppConfig):  # type: ignore[misc]
    """App config for the api-response-toolkit Django integration."""

    name = "api_response_toolkit.django"
    label = "api_response_toolkit"
    verbose_name = "API Response Toolkit"

    default_auto_field: str = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """Called when Django is ready; currently a no-op placeholder."""
        # Intentionally minimal — no signals or checks to register.
        return None


__all__ = ["ApiResponseToolkitConfig"]
