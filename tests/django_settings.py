"""Minimal Django settings for testing the Django/DRF integrations."""

from __future__ import annotations

SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = False
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "api_response_toolkit.django",
]

MIDDLEWARE = [
    "api_response_toolkit.django.middleware.APIExceptionMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "api_response_toolkit.drf.exception_handler.api_exception_handler",
    "DEFAULT_PAGINATION_CLASS": (
        "api_response_toolkit.drf.pagination.StandardizedPageNumberPagination"
    ),
    "PAGE_SIZE": 20,
}

ROOT_URLCONF = "tests.urls"
