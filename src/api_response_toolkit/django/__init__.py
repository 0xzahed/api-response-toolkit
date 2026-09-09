"""Django integration for api-response-toolkit.

Importing this package requires Django to be installed. The functions here
wrap the core response builders and return Django ``JsonResponse`` objects.
"""

from __future__ import annotations

from .responses import (
    error,
    paginated,
    success,
    validation_error,
)

__all__ = [
    "error",
    "paginated",
    "success",
    "validation_error",
]
