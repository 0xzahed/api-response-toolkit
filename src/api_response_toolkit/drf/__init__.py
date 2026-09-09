"""Django REST Framework integration for api-response-toolkit.

Importing this package requires both Django and Django REST Framework to be
installed. The functions here wrap the core response builders and return DRF
``Response`` objects.
"""

from __future__ import annotations

from .exception_handler import api_exception_handler
from .pagination import StandardizedPageNumberPagination
from .responses import (
    error,
    paginated,
    success,
    validation_error,
)

__all__ = [
    "StandardizedPageNumberPagination",
    "api_exception_handler",
    "error",
    "paginated",
    "success",
    "validation_error",
]
