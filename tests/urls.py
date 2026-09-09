"""URL configuration for test views used by Django/DRF tests."""

from __future__ import annotations

from django.urls import path  # type: ignore[import-not-found]

from .views_for_tests import (
    drf_success_view,
    drf_unhandled_view,
    drf_validation_view,
    plain_django_success_view,
    plain_django_unhandled_view,
)

urlpatterns = [
    path("plain/success/", plain_django_success_view),
    path("plain/unhandled/", plain_django_unhandled_view),
    path("drf/success/", drf_success_view),
    path("drf/validation/", drf_validation_view),
    path("drf/unhandled/", drf_unhandled_view),
]
