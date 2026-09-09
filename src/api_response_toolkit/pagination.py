"""Pagination helpers for the core (framework-agnostic) package.

This module re-exports the pagination utilities from :mod:`response` so they
are discoverable as ``api_response_toolkit.pagination``. The DRF integration
provides its own pagination class in :mod:`api_response_toolkit.drf.pagination`.
"""

from __future__ import annotations

from .response import build_pagination, calculate_total_pages
from .types import PaginationMeta

__all__ = [
    "PaginationMeta",
    "build_pagination",
    "calculate_total_pages",
]
