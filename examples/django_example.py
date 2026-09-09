"""Django integration example.

This example shows how to use the toolkit inside a plain Django view. It
requires Django to be installed::

    pip install "api-response-toolkit[django]"

To run as a minimal project, configure ``settings.py`` with::

    INSTALLED_APPS = [
        ...,
        "api_response_toolkit.django",
    ]
    MIDDLEWARE = [
        ...,
        "api_response_toolkit.django.middleware.APIExceptionMiddleware",
    ]
"""

from __future__ import annotations

from django.http import HttpRequest  # type: ignore[import-not-found]

from api_response_toolkit import NotFoundError
from api_response_toolkit.django import error, paginated, success, validation_error


def list_users(request: HttpRequest):
    """Return a paginated list of users as a standardized JsonResponse."""
    users = [{"id": 1, "name": "Abu"}, {"id": 2, "name": "Sara"}]
    return paginated(
        data=users,
        page=1,
        limit=20,
        total=125,
        message="Users fetched successfully",
    )


def get_user(request: HttpRequest, user_id: int):
    """Return a single user or raise a NotFoundError (handled by middleware)."""
    if user_id != 1:
        raise NotFoundError(message="User not found", code="USER_NOT_FOUND")
    return success(message="User fetched successfully", data={"id": 1, "name": "Abu"})


def create_user(request: HttpRequest):
    """Create a user, returning validation errors for bad input."""
    if not request.POST.get("email"):
        return validation_error(errors={"email": ["This field is required."]})
    return success(
        message="User created successfully",
        data={"id": 1, "name": "Abu"},
        status_code=201,
    )


def delete_user(request: HttpRequest, user_id: int):
    """Return an error response for a forbidden action."""
    return error(
        message="You do not have permission to delete this user.",
        code="FORBIDDEN",
        status_code=403,
    )
