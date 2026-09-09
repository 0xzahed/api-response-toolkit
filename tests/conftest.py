"""Root pytest configuration.

Sets up the ``src/`` layout import path and configures Django for the
pytest-django plugin. The Django/DRF integration tests rely on this; the
core tests are unaffected because ``API_RESPONSE_TOOLKIT`` is not set in the
test settings, so ``get_config()`` falls back to the in-memory config.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.django_settings")

import django  # noqa: E402
from django.apps import apps as django_apps  # noqa: E402

if not django_apps.ready:
    django.setup()


import pytest  # noqa: E402

from api_response_toolkit import reset_config  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_toolkit_config():
    """Reset the toolkit config to defaults before and after every test."""
    reset_config()
    yield
    reset_config()
