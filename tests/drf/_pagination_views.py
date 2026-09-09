"""Views and URLs for the DRF pagination test."""

from __future__ import annotations

from django.urls import path  # type: ignore[import-not-found]
from rest_framework import generics, serializers  # type: ignore[import-not-found]

from api_response_toolkit.drf.pagination import StandardizedPageNumberPagination

items = [{"id": i, "name": f"item-{i}"} for i in range(1, 51)]


class ItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ItemListAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = StandardizedPageNumberPagination

    def get_queryset(self):
        return items


urlpatterns = [
    path("items/", ItemListAPIView.as_view()),
]
