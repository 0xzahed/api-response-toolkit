# api-response-toolkit

[![PyPI version](https://img.shields.io/pypi/v/api-response-toolkit.svg)](https://pypi.org/project/api-response-toolkit/)
[![Python versions](https://img.shields.io/pypi/pyversions/api-response-toolkit.svg)](https://pypi.org/project/api-response-toolkit/)
[![Tests](https://github.com/0xzahed/api-response-toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/0xzahed/api-response-toolkit/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/0xzahed/api-response-toolkit/main/.coverage-badge.json)](https://github.com/0xzahed/api-response-toolkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **lightweight, clean, extensible API response standardization toolkit** for
Python, Django, and Django REST Framework.

Create consistent success, error, validation, pagination, and exception
responses with a simple, predictable API. The core package works with plain
Python — Django and DRF are optional integrations.

---

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core API](#core-api)
  - [Success Responses](#success-responses)
  - [Error Responses](#error-responses)
  - [Validation Errors](#validation-errors)
  - [Pagination](#pagination)
  - [Metadata](#metadata)
- [Exceptions](#exceptions)
- [Django Integration](#django-integration)
- [DRF Integration](#drf-integration)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Roadmap](#roadmap)

---

## Description

`api-response-toolkit` helps you produce **consistent JSON API responses**
across your entire application. Instead of every endpoint inventing its own
response shape, the toolkit enforces a single, predictable envelope:

```json
{
    "success": true,
    "message": "User fetched successfully",
    "data": { "id": 1, "name": "Abu" }
}
```

For errors:

```json
{
    "success": false,
    "message": "User not found",
    "code": "USER_NOT_FOUND"
}
```

The core package has **zero required dependencies** and works with any Python
3.9+ project. Optional integrations provide first-class support for Django
(`JsonResponse`) and Django REST Framework (`Response`).

## Features

- **Simple, predictable API** — `success()`, `error()`, `validation_error()`, `paginated()`
- **Standardized response envelope** for all responses
- **Custom exception hierarchy** with structured error fields
- **Pagination helpers** with automatic `total_pages` calculation
- **Optional metadata** support
- **HTTP status code validation**
- **Django integration** — returns `JsonResponse` objects
- **Django middleware** for unhandled API exceptions (safe in production)
- **DRF integration** — returns `Response` objects
- **Custom DRF exception handler** normalizing all DRF exceptions
- **Standardized DRF pagination class**
- **Centralized configuration** (pure Python or Django settings)
- **Fully typed** — ships with `py.typed`, passes `mypy --strict`
- **98% test coverage**, Ruff-clean, no required dependencies

## Installation

```bash
# Core only (no Django/DRF)
pip install api-response-toolkit

# With Django support
pip install "api-response-toolkit[django]"

# With Django REST Framework support
pip install "api-response-toolkit[drf]"

# Everything
pip install "api-response-toolkit[all]"
```

| Extra | Dependencies |
|-------|-------------|
| `django` | Django >= 4.2 |
| `drf` | Django >= 4.2, djangorestframework >= 3.14 |
| `all` | Django >= 4.2, djangorestframework >= 3.14 |
| `dev` | pytest, pytest-cov, pytest-django, ruff, mypy, build, twine |

## Quick Start

```python
from api_response_toolkit import success, error

# Success response
response = success(
    message="User created successfully",
    data={"id": 1, "name": "Abu"},
    status_code=201,
)

# Error response
response = error(
    message="User not found",
    code="USER_NOT_FOUND",
    status_code=404,
)
```

In a Django view:

```python
from api_response_toolkit.django import success

def get_user(request):
    return success(message="User fetched successfully", data={"id": 1})
```

In a DRF view:

```python
from api_response_toolkit.drf import success
from rest_framework.views import APIView

class UserView(APIView):
    def get(self, request):
        return success(message="User fetched successfully", data={"id": 1})
```

## Core API

### Success Responses

```python
from api_response_toolkit import success, to_dict

# Minimal
payload = success()
# {"success": true, "message": "Success"}

# With data
payload = success(message="User fetched successfully", data={"id": 1, "name": "Abu"})
# {"success": true, "message": "User fetched successfully", "data": {"id": 1, "name": "Abu"}}

# With custom status code
payload = success(message="Created", data={"id": 1}, status_code=201)

# Serialize to dict
body = to_dict(payload)
```

Optional fields (`data`, `code`, `errors`, `details`, `meta`, `pagination`)
are **omitted when `None`** to keep responses compact.

### Error Responses

```python
from api_response_toolkit import error

response = error(
    message="User not found",
    code="USER_NOT_FOUND",
    status_code=404,
)
# {"success": false, "message": "User not found", "code": "USER_NOT_FOUND"}
```

With field-level errors:

```python
response = error(
    message="Validation failed",
    code="VALIDATION_ERROR",
    status_code=400,
    errors={
        "email": ["This field is required."],
        "password": ["Password is too short."],
    },
)
```

Supported parameters: `message`, `code`, `status_code`, `data`, `errors`,
`details`, `meta`. When `code` is omitted, a sensible default is derived from
the status code (e.g. 404 → `"NOT_FOUND"`).

### Validation Errors

A dedicated helper for validation failures:

```python
from api_response_toolkit import validation_error

response = validation_error(
    errors={
        "email": ["Invalid email address"],
        "username": ["Username already exists"],
    },
)
# {
#     "success": false,
#     "message": "Validation failed",
#     "code": "VALIDATION_ERROR",
#     "errors": {
#         "email": ["Invalid email address"],
#         "username": ["Username already exists"]
#     }
# }
```

Customize the message, code, or status code:

```python
validation_error(
    errors={"email": ["Invalid"]},
    message="Please fix the errors below",
    code="CUSTOM_VALIDATION",
    status_code=422,
)
```

### Pagination

Use the `paginated` helper — `total_pages` is calculated automatically:

```python
from api_response_toolkit import paginated

response = paginated(
    data=users,
    page=1,
    limit=20,
    total=125,
)
# {
#     "success": true,
#     "message": "Success",
#     "data": [...],
#     "pagination": {
#         "page": 1,
#         "limit": 20,
#         "total": 125,
#         "total_pages": 7
#     }
# }
```

Edge cases are handled safely:

- `total = 0` → `total_pages = 0`
- `limit = 0` → `total_pages = 0` (no division by zero)
- Negative `page`/`limit` are clamped to `1`/`0`

### Metadata

```python
response = success(
    message="Success",
    data={"id": 1},
    meta={
        "request_id": "abc123",
        "version": "v1",
    },
)
# {
#     "success": true,
#     "message": "Success",
#     "data": {"id": 1},
#     "meta": {"request_id": "abc123", "version": "v1"}
# }
```

## Exceptions

The toolkit provides a custom exception hierarchy. Each exception carries
structured fields (`message`, `code`, `status_code`, `errors`, `details`,
`metadata`) so middleware and exception handlers can produce consistent
responses automatically.

```python
from api_response_toolkit import (
    APIException,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
)

raise NotFoundError(message="User not found", code="USER_NOT_FOUND")
raise ValidationError(errors={"email": ["Invalid email address"]})
raise ForbiddenError(message="Access denied")
```

| Exception | Default Status | Default Code |
|-----------|---------------|--------------|
| `APIException` | 500 | `API_ERROR` |
| `NotFoundError` | 404 | `NOT_FOUND` |
| `UnauthorizedError` | 401 | `UNAUTHORIZED` |
| `ForbiddenError` | 403 | `FORBIDDEN` |
| `ValidationError` | 400 | `VALIDATION_ERROR` |
| `BadRequestError` | 400 | `BAD_REQUEST` |
| `ConflictError` | 409 | `CONFLICT` |
| `InternalServerError` | 500 | `INTERNAL_ERROR` |

Use `from_status_code()` to construct the most specific exception for a
status code:

```python
from api_response_toolkit import from_status_code

exc = from_status_code(404, message="User not found")
# Returns a NotFoundError instance
```

## Django Integration

Install with the `django` extra:

```bash
pip install "api-response-toolkit[django]"
```

Add to your `INSTALLED_APPS` and `MIDDLEWARE`:

```python
INSTALLED_APPS = [
    # ...
    "api_response_toolkit.django",
]

MIDDLEWARE = [
    # ...
    "api_response_toolkit.django.middleware.APIExceptionMiddleware",
]
```

Use in views — returns Django `JsonResponse` objects:

```python
from api_response_toolkit.django import success, error, validation_error, paginated

def list_users(request):
    return success(message="Users fetched successfully", data=[{"id": 1}])

def get_user(request, user_id):
    return success(message="User fetched", data={"id": user_id})

def create_user(request):
    return success(message="Created", data={"id": 1}, status_code=201)

def delete_user(request, user_id):
    return error(message="Forbidden", code="FORBIDDEN", status_code=403)
```

### Django Middleware

The `APIExceptionMiddleware` catches unhandled exceptions and converts them
to standardized JSON responses. It only intervenes for **API requests**
(path starting with `/api/` or `application/json` content/accept type), so
Django's normal HTML pages are preserved for non-API requests.

Toolkit `APIException` subclasses are always converted regardless of the
request type.

Configuration via `settings.API_RESPONSE_TOOLKIT`:

```python
API_RESPONSE_TOOLKIT = {
    "middleware_enabled": True,       # enable/disable
    "middleware_debug": False,         # override debug behavior
    "include_traceback": False,        # include tracebacks when debug
    "custom_error_handler": None,      # dotted path to a callable
}
```

**Security**: When `DEBUG=False`, unexpected exceptions return a safe generic
`"Internal server error"` message — stack traces and internal details are
never exposed.

## DRF Integration

Install with the `drf` extra:

```bash
pip install "api-response-toolkit[drf]"
```

Configure in `settings.py`:

```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "api_response_toolkit.drf.exception_handler.api_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "api_response_toolkit.drf.pagination.StandardizedPageNumberPagination",
    "PAGE_SIZE": 20,
}
```

Use in views — returns DRF `Response` objects:

```python
from api_response_toolkit.drf import success, error, validation_error, paginated
from rest_framework.views import APIView

class UserView(APIView):
    def get(self, request):
        return success(message="Users fetched successfully", data=[{"id": 1}])

    def post(self, request):
        if not request.data.get("email"):
            return validation_error(errors={"email": ["This field is required."]})
        return success(message="Created", data={"id": 1}, status_code=201)
```

### DRF Exception Handler

The custom exception handler normalizes all DRF built-in exceptions into the
toolkit's envelope:

| DRF Exception | Code |
|--------------|------|
| `ValidationError` | `VALIDATION_ERROR` |
| `NotFound` | `NOT_FOUND` |
| `PermissionDenied` | `FORBIDDEN` |
| `NotAuthenticated` | `NOT_AUTHENTICATED` |
| `AuthenticationFailed` | `AUTHENTICATION_FAILED` |
| `ParseError` | `PARSE_ERROR` |
| `Throttled` | `RATE_LIMITED` |
| `MethodNotAllowed` | `METHOD_NOT_ALLOWED` |
| `UnsupportedMediaType` | `UNSUPPORTED_MEDIA_TYPE` |
| `APIException` (generic) | derived from `detail.code` |
| Django `Http404` | `NOT_FOUND` |
| Django `PermissionDenied` | `FORBIDDEN` |
| Unexpected | `INTERNAL_ERROR` |

Example validation response:

```json
{
    "success": false,
    "message": "Validation failed",
    "code": "VALIDATION_ERROR",
    "errors": {
        "email": ["Enter a valid email address."]
    }
}
```

### DRF Pagination

The `StandardizedPageNumberPagination` class produces the toolkit's envelope
automatically:

```json
{
    "success": true,
    "message": "Success",
    "data": [...],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 125,
        "total_pages": 7
    }
}
```

## Configuration

The toolkit works with zero configuration. For customization, use either the
pure-Python `configure()` function or Django settings.

### Pure Python

```python
from api_response_toolkit import configure

configure(
    default_success_message="Success",
    default_error_message="Something went wrong",
    include_meta=True,
    include_null_data=False,
    debug=False,
    include_traceback=False,
)
```

### Django Settings

```python
# settings.py
API_RESPONSE_TOOLKIT = {
    "DEFAULT_SUCCESS_MESSAGE": "Success",
    "DEFAULT_ERROR_MESSAGE": "Something went wrong",
    "INCLUDE_META": True,
    "INCLUDE_NULL_DATA": False,
    "DEBUG": False,
}
```

Keys are matched **case-insensitively**. Unknown keys are preserved in the
`extra` mapping for custom use.

| Key | Default | Description |
|-----|---------|-------------|
| `default_success_message` | `"Success"` | Default success message |
| `default_error_message` | `"Something went wrong"` | Default error message |
| `include_meta` | `True` | Include `meta` field when present |
| `include_null_data` | `False` | Include `data` field when `None` |
| `debug` | `False` | Show internal details in error responses |
| `include_traceback` | `False` | Include tracebacks when debug is on |

## Error Handling

The toolkit distinguishes between **expected** and **unexpected** errors:

- **Expected errors** (toolkit `APIException` subclasses, DRF exceptions):
  structured fields are preserved in the response.
- **Unexpected errors** (any other exception): a safe generic 500 response is
  returned. When `DEBUG=True`, the exception type and message are included
  for debugging; when `DEBUG=False`, only `"Internal server error"` is
  shown.

Stack traces are **never** exposed in production unless explicitly enabled
via `include_traceback=True` **and** `debug=True`.

## Examples

Working examples are in the [`examples/`](examples/) directory:

- [`examples/basic.py`](examples/basic.py) — core usage (no Django/DRF)
- [`examples/django_example.py`](examples/django_example.py) — Django views
- [`examples/drf_example.py`](examples/drf_example.py) — DRF views

Run the basic example:

```bash
python -m examples.basic
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=api_response_toolkit --cov-report=term-missing

# Lint
ruff check src tests examples

# Type check
mypy src/api_response_toolkit
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards,
and the pull request process.

## License

This project is licensed under the [MIT License](LICENSE).

## Roadmap

- [ ] Async support (Starlette / FastAPI integration)
- [ ] Flask integration
- [ ] OpenAPI / Schema generation helpers
- [ ] Localization of default messages
- [ ] Pluggable response envelope customization
- [ ] Request ID middleware integration
