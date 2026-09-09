"""api-response-toolkit: a lightweight API response standardization toolkit.

The core package is framework-agnostic and works with plain Python. Optional
Django and Django REST Framework integrations are available via the
``api-response-toolkit[django]`` and ``api-response-toolkit[drf]`` extras.

Quick start::

    from api_response_toolkit import success, error

    return success(message="User created", data={"id": 1})
    return error(message="User not found", code="USER_NOT_FOUND", status_code=404)
"""

from __future__ import annotations

from .config import configure, get_config, reset_config
from .errors import (
    BAD_REQUEST,
    CONFLICT,
    FORBIDDEN,
    INTERNAL_ERROR,
    METHOD_NOT_ALLOWED,
    NOT_FOUND,
    NOT_IMPLEMENTED,
    PARSE_ERROR,
    RATE_LIMITED,
    SERVICE_UNAVAILABLE,
    STATUS_CODE_TO_CODE,
    TIMEOUT,
    UNAUTHORIZED,
    UNSUPPORTED_MEDIA_TYPE,
    VALIDATION_ERROR,
    code_for_status,
)
from .exceptions import (
    APIException,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
    from_status_code,
)
from .pagination import PaginationMeta
from .response import (
    build_pagination,
    calculate_total_pages,
    error,
    paginated,
    success,
    to_dict,
    validation_error,
)
from .types import ResponsePayload, ToolkitConfig

__version__ = "0.1.0"

__all__ = [
    "APIException",
    "BAD_REQUEST",
    "BadRequestError",
    "CONFLICT",
    "ConflictError",
    "FORBIDDEN",
    "ForbiddenError",
    "INTERNAL_ERROR",
    "InternalServerError",
    "METHOD_NOT_ALLOWED",
    "NOT_FOUND",
    "NOT_IMPLEMENTED",
    "NotFoundError",
    "PARSE_ERROR",
    "PaginationMeta",
    "RATE_LIMITED",
    "ResponsePayload",
    "SERVICE_UNAVAILABLE",
    "STATUS_CODE_TO_CODE",
    "TIMEOUT",
    "ToolkitConfig",
    "UNAUTHORIZED",
    "UNSUPPORTED_MEDIA_TYPE",
    "UnauthorizedError",
    "VALIDATION_ERROR",
    "ValidationError",
    "__version__",
    "build_pagination",
    "calculate_total_pages",
    "code_for_status",
    "configure",
    "error",
    "from_status_code",
    "get_config",
    "paginated",
    "reset_config",
    "success",
    "to_dict",
    "validation_error",
]
