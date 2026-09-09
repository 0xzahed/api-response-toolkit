"""Test views exercising the Django and DRF integrations."""

from __future__ import annotations

from django.http import HttpRequest  # type: ignore[import-not-found]
from rest_framework.request import Request  # type: ignore[import-not-found]
from rest_framework.response import Response  # type: ignore[import-not-found]
from rest_framework.views import APIView  # type: ignore[import-not-found]

from api_response_toolkit import NotFoundError
from api_response_toolkit.django import success as django_success
from api_response_toolkit.drf import success as drf_success


def plain_django_success_view(request: HttpRequest):
    """Plain Django view returning a standardized JsonResponse."""
    return django_success(message="Users fetched successfully", data=[{"id": 1}])


def plain_django_unhandled_view(request: HttpRequest):
    """Plain Django view that raises a NotFoundError."""
    raise NotFoundError(message="User not found", code="USER_NOT_FOUND")


class DRFSuccessView(APIView):
    def get(self, request: Request) -> Response:
        return drf_success(message="Users fetched successfully", data=[{"id": 1}])


drf_success_view = DRFSuccessView.as_view()


class DRFValidationView(APIView):
    def get(self, request: Request) -> Response:
        from rest_framework.exceptions import ValidationError  # type: ignore[import-not-found]

        raise ValidationError({"email": ["Enter a valid email address."]})


drf_validation_view = DRFValidationView.as_view()


class DRFUnhandledView(APIView):
    def get(self, request: Request) -> Response:
        raise RuntimeError("boom")


drf_unhandled_view = DRFUnhandledView.as_view()
