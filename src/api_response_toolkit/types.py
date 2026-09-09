"""Type definitions for the api-response-toolkit package."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Union

# Public type aliases used across the package.
JSONScalar = Union[str, int, float, bool, None]
JSONValue = Union[JSONScalar, list[Any], dict[str, Any]]
JSONDict = dict[str, Any]
ErrorMapping = Mapping[str, Union[str, list[str], "ErrorMapping"]]


@dataclass(frozen=True)
class PaginationMeta:
    """Structured pagination metadata.

    Attributes:
        page: Current page number (1-based).
        limit: Number of items per page.
        total: Total number of items across all pages.
        total_pages: Total number of pages, derived from ``total`` and ``limit``.
    """

    page: int
    limit: int
    total: int
    total_pages: int

    def to_dict(self) -> JSONDict:
        """Convert the pagination metadata to a plain dictionary."""
        return {
            "page": self.page,
            "limit": self.limit,
            "total": self.total,
            "total_pages": self.total_pages,
        }


@dataclass
class ResponsePayload:
    """A normalized API response payload.

    This dataclass represents the canonical shape of every response produced
    by the toolkit. It is intentionally framework-agnostic so it can be
    serialized to JSON, wrapped in a Django ``JsonResponse``, or returned as a
    DRF ``Response``.
    """

    success: bool
    message: str
    data: Any = None
    code: str | None = None
    errors: JSONDict | None = None
    details: Any | None = None
    meta: JSONDict | None = None
    pagination: JSONDict | None = None
    status_code: int = 200

    def to_dict(self, *, include_null_data: bool = False, include_meta: bool = True) -> JSONDict:
        """Serialize the payload to a JSON-serializable dictionary.

        Optional fields (``code``, ``errors``, ``details``, ``meta``,
        ``pagination``) are omitted when they are ``None`` to keep responses
        compact and predictable.

        Args:
            include_null_data: When ``True``, always include the ``data`` key
                even if it is ``None``.
            include_meta: When ``False``, omit the ``meta`` key even if it has
                a value.

        Returns:
            A dictionary ready for JSON serialization.
        """
        payload: JSONDict = {
            "success": self.success,
            "message": self.message,
        }

        if self.data is not None or include_null_data:
            payload["data"] = self.data

        if self.code is not None:
            payload["code"] = self.code

        if self.errors is not None:
            payload["errors"] = self.errors

        if self.details is not None:
            payload["details"] = self.details

        if self.meta is not None and include_meta:
            payload["meta"] = self.meta

        if self.pagination is not None:
            payload["pagination"] = self.pagination

        return payload


@dataclass(frozen=True)
class ToolkitConfig:
    """Immutable configuration for the toolkit.

    Attributes:
        default_success_message: Message used when no message is provided for
            success responses.
        default_error_message: Message used when no message is provided for
            error responses.
        include_meta: Whether to include the ``meta`` key when it has a value.
        include_null_data: Whether to include the ``data`` key when it is null.
        debug: When ``True``, exception responses may include tracebacks and
            internal details. Never enable this in production.
        include_traceback: Whether to include tracebacks in exception
            responses when ``debug`` is enabled.
    """

    default_success_message: str = "Success"
    default_error_message: str = "Something went wrong"
    include_meta: bool = True
    include_null_data: bool = False
    debug: bool = False
    include_traceback: bool = False
    extra: Mapping[str, Any] = field(default_factory=dict)


__all__ = [
    "ErrorMapping",
    "JSONDict",
    "JSONScalar",
    "JSONValue",
    "PaginationMeta",
    "ResponsePayload",
    "ToolkitConfig",
]
