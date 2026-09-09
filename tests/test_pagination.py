"""Tests for the pagination helpers."""

from __future__ import annotations

import pytest

from api_response_toolkit import build_pagination, calculate_total_pages
from api_response_toolkit.pagination import PaginationMeta


class TestCalculateTotalPages:
    @pytest.mark.parametrize(
        "total, limit, expected",
        [
            (0, 20, 0),
            (100, 0, 0),
            (100, 20, 5),
            (101, 20, 6),
            (1, 20, 1),
            (20, 20, 1),
            (21, 20, 2),
            (125, 20, 7),
            (100, 25, 4),
            (95, 10, 10),
        ],
    )
    def test_calculations(self, total, limit, expected):
        assert calculate_total_pages(total, limit) == expected

    def test_negative_total_clamped(self):
        assert calculate_total_pages(-10, 20) == 0

    def test_negative_limit_clamped(self):
        assert calculate_total_pages(100, -5) == 0


class TestBuildPagination:
    def test_basic(self):
        result = build_pagination(page=1, limit=20, total=125)
        assert result == {
            "page": 1,
            "limit": 20,
            "total": 125,
            "total_pages": 7,
        }

    def test_negative_page_clamped(self):
        result = build_pagination(page=-3, limit=10, total=100)
        assert result["page"] == 1

    def test_negative_limit_clamped(self):
        result = build_pagination(page=1, limit=-10, total=100)
        assert result["limit"] == 0
        assert result["total_pages"] == 0

    def test_zero_total(self):
        result = build_pagination(page=1, limit=20, total=0)
        assert result["total_pages"] == 0

    def test_zero_limit(self):
        result = build_pagination(page=1, limit=0, total=100)
        assert result["total_pages"] == 0

    def test_keys_present(self):
        result = build_pagination(page=2, limit=15, total=50)
        assert set(result.keys()) == {"page", "limit", "total", "total_pages"}


class TestPaginationMeta:
    def test_to_dict(self):
        meta = PaginationMeta(page=1, limit=10, total=30, total_pages=3)
        assert meta.to_dict() == {
            "page": 1,
            "limit": 10,
            "total": 30,
            "total_pages": 3,
        }

    def test_frozen(self):
        meta = PaginationMeta(page=1, limit=10, total=30, total_pages=3)
        with pytest.raises(Exception):  # noqa: B017 - FrozenInstanceError subclass
            meta.page = 5  # type: ignore[misc]
