"""DRF pagination classes producing standardized response envelopes.

Use these by configuring them in ``REST_FRAMEWORK``::

    REST_FRAMEWORK = {
        "DEFAULT_PAGINATION_CLASS":
            "api_response_toolkit.drf.pagination.StandardizedPageNumberPagination",
        "PAGE_SIZE": 20,
    }
"""

from __future__ import annotations

from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from ..config import get_config
from ..response import build_pagination


class StandardizedPageNumberPagination(PageNumberPagination):  # type: ignore[misc]
    """Page-number pagination that emits the toolkit's standardized envelope.

    The response body is::

        {
            "success": true,
            "message": "Data fetched successfully",
            "data": [...],
            "pagination": {
                "page": 1,
                "limit": 20,
                "total": 125,
                "total_pages": 7
            }
        }
    """

    page_size_query_param = "limit"
    max_page_size = 1000

    def get_paginated_response(self, data: Any) -> Response:
        """Return a DRF ``Response`` with the standardized envelope."""
        config = get_config()
        page = self.page.number
        limit = self.get_page_size(self.request)
        limit = int(limit) if limit is not None else int(self.page_size)
        total = self.page.paginator.count
        pagination = build_pagination(page=page, limit=limit, total=total)
        body = {
            "success": True,
            "message": config.default_success_message,
            "data": data,
            "pagination": pagination,
        }
        return Response(body)


__all__ = ["StandardizedPageNumberPagination"]
