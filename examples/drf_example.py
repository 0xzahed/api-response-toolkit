"""Django REST Framework integration example.

This example shows how to use the toolkit inside a DRF view. It requires
Django and DRF to be installed::

    pip install "api-response-toolkit[drf]"

Configure the exception handler in ``settings.py``::

    REST_FRAMEWORK = {
        "EXCEPTION_HANDLER":
            "api_response_toolkit.drf.exception_handler.api_exception_handler",
        "DEFAULT_PAGINATION_CLASS":
            "api_response_toolkit.drf.pagination.StandardizedPageNumberPagination",
        "PAGE_SIZE": 20,
    }
"""

from __future__ import annotations

from rest_framework.request import Request  # type: ignore[import-not-found]
from rest_framework.views import APIView  # type: ignore[import-not-found]

from api_response_toolkit import NotFoundError
from api_response_toolkit.drf import error, paginated, success, validation_error


class UserListView(APIView):
    """List users with a standardized paginated response."""

    def get(self, request: Request):
        users = [{"id": 1, "name": "Abu"}, {"id": 2, "name": "Sara"}]
        return paginated(
            data=users,
            page=1,
            limit=20,
            total=125,
            message="Users fetched successfully",
        )

    def post(self, request: Request):
        email = request.data.get("email")
        if not email:
            return validation_error(errors={"email": ["This field is required."]})
        return success(
            message="User created successfully",
            data={"id": 1, "email": email},
            status_code=201,
        )


class UserDetailView(APIView):
    """Retrieve a single user."""

    def get(self, request: Request, user_id: int):
        if user_id != 1:
            raise NotFoundError(message="User not found", code="USER_NOT_FOUND")
        return success(message="User fetched successfully", data={"id": 1, "name": "Abu"})

    def delete(self, request: Request, user_id: int):
        return error(
            message="You do not have permission to delete this user.",
            code="FORBIDDEN",
            status_code=403,
        )
