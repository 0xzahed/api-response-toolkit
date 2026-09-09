"""Tests for the DRF pagination class."""

from __future__ import annotations

import json

from django.conf import settings  # type: ignore[import-not-found]
from django.test import Client  # type: ignore[import-not-found]


class TestDRFPagination:
    def test_pagination_envelope(self):
        """Verify the standardized pagination envelope via a paginated view."""
        old_urls = settings.ROOT_URLCONF
        try:
            settings.ROOT_URLCONF = "tests.drf._pagination_views"
            client = Client()
            resp = client.get("/items/?page=1&limit=10")
            assert resp.status_code == 200
            body = json.loads(resp.content)
            assert body["success"] is True
            assert body["pagination"] == {
                "page": 1,
                "limit": 10,
                "total": 50,
                "total_pages": 5,
            }
            assert len(body["data"]) == 10
        finally:
            settings.ROOT_URLCONF = old_urls

    def test_pagination_second_page(self):
        old_urls = settings.ROOT_URLCONF
        try:
            settings.ROOT_URLCONF = "tests.drf._pagination_views"
            client = Client()
            resp = client.get("/items/?page=2&limit=10")
            assert resp.status_code == 200
            body = json.loads(resp.content)
            assert body["pagination"]["page"] == 2
            assert len(body["data"]) == 10
        finally:
            settings.ROOT_URLCONF = old_urls
