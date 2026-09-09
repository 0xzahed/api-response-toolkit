# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-09

### Added

- Initial release of `api-response-toolkit`.
- Core (framework-agnostic) response builders: `success`, `error`,
  `validation_error`, `paginated`.
- Custom exception hierarchy: `APIException`, `NotFoundError`,
  `UnauthorizedError`, `ForbiddenError`, `ValidationError`,
  `BadRequestError`, `ConflictError`, `InternalServerError`.
- Pagination helpers: `build_pagination`, `calculate_total_pages`.
- Centralized configuration via `configure()` / `get_config()`.
- Optional Django integration returning `JsonResponse` objects.
- Optional Django middleware for unhandled API exceptions.
- Optional Django REST Framework integration returning `Response` objects.
- Custom DRF exception handler producing standardized envelopes.
- Standardized DRF pagination class.
- Comprehensive test suite with 98% coverage.
- GitHub Actions CI workflow (Python 3.9–3.13).
- GitHub Actions PyPI publishing workflow using trusted publishing.
- Examples for core, Django, and DRF usage.

[Unreleased]: https://github.com/0xzahed/api-response-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/0xzahed/api-response-toolkit/releases/tag/v0.1.0
