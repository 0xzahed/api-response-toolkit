# Contributing

Thank you for your interest in contributing to **api-response-toolkit**! This
document outlines the process for contributing bug reports, fixes, and new
features.

## Getting Started

1. Fork the repository and clone your fork locally.
2. Install the package in editable mode with development dependencies:

   ```bash
   pip install -e ".[dev,all]"
   ```

3. Create a branch for your work:

   ```bash
   git checkout -b fix/my-bugfix
   ```

## Development Workflow

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=api_response_toolkit --cov-report=term-missing
```

### Linting

```bash
ruff check src tests examples
```

### Type Checking

```bash
mypy src/api_response_toolkit
```

### Building

```bash
python -m build
twine check dist/*
```

## Coding Standards

- Follow **PEP 8** (enforced by Ruff).
- Use **type hints** on all public functions.
- Write **docstrings** for all public modules, classes, and functions.
- Keep the **core package free** of Django/DRF imports — those belong in the
  `django/` and `drf/` subpackages only.
- Avoid introducing unnecessary dependencies.
- Write tests for any new functionality. Target **90%+ coverage**.

## Pull Request Process

1. Ensure all tests, linting, and type checks pass locally.
2. Add a changelog entry under `[Unreleased]` in `CHANGELOG.md`.
3. Keep your PR focused — one feature or fix per PR is ideal.
4. Use clear, descriptive commit messages.
5. Reference any related issues in your PR description.

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: incompatible API changes.
- **MINOR**: backward-compatible new functionality.
- **PATCH**: backward-compatible bug fixes.

## Reporting Issues

- Use [GitHub Issues](https://github.com/0xzahed/api-response-toolkit/issues)
  to report bugs or request features.
- Include a minimal reproduction case when reporting bugs.
- Do **not** report security vulnerabilities in public issues — see the
  security policy below.

## Security

If you discover a security vulnerability, please email the maintainer
privately rather than opening a public issue. Include a description of the
issue and, if possible, a proof of concept.

## License

By contributing, you agree that your contributions will be licensed under the
MIT License.
