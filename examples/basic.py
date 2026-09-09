"""Basic usage examples for the core (framework-agnostic) package.

Run with::

    python -m examples.basic

No Django or DRF installation required.
"""

from __future__ import annotations

import json

from api_response_toolkit import (
    NotFoundError,
    ValidationError,
    error,
    paginated,
    success,
    to_dict,
    validation_error,
)


def show(label: str, payload) -> None:
    """Print a labeled JSON representation of a payload."""
    print(f"\n=== {label} ===")
    print(json.dumps(to_dict(payload), indent=2, default=str))


def main() -> None:
    # --- Success responses -------------------------------------------------
    show("Minimal success", success())
    show(
        "Success with data",
        success(message="User fetched successfully", data={"id": 1, "name": "Abu"}),
    )
    show(
        "Created (201)",
        success(message="User created successfully", data={"id": 1}, status_code=201),
    )

    # --- Error responses ---------------------------------------------------
    show("Not found error", error(message="User not found", code="USER_NOT_FOUND", status_code=404))
    show(
        "Validation error response",
        error(
            message="Validation failed",
            code="VALIDATION_ERROR",
            status_code=400,
            errors={
                "email": ["This field is required."],
                "password": ["Password is too short."],
            },
        ),
    )

    # --- Validation helper ------------------------------------------------
    show(
        "validation_error helper",
        validation_error(
            errors={
                "email": ["Invalid email address"],
                "username": ["Username already exists"],
            }
        ),
    )

    # --- Pagination --------------------------------------------------------
    users = [{"id": i, "name": f"User {i}"} for i in range(1, 6)]
    show("Paginated", paginated(data=users, page=1, limit=20, total=125))

    # --- Metadata ----------------------------------------------------------
    show(
        "With metadata",
        success(data={"id": 1}, meta={"request_id": "abc123", "version": "v1"}),
    )

    # --- Exceptions --------------------------------------------------------
    try:
        raise NotFoundError(message="User not found", code="USER_NOT_FOUND")
    except NotFoundError as exc:
        print("\n=== Exception payload ===")
        print(json.dumps(exc.to_payload(), indent=2))

    try:
        raise ValidationError(errors={"email": ["Invalid email address"]})
    except ValidationError as exc:
        print("\n=== Caught ValidationError ===")
        print(f"message={exc.message!r} code={exc.code!r} status={exc.status_code}")
        print(json.dumps(exc.to_payload(), indent=2))


if __name__ == "__main__":
    main()
