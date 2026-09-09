"""Tests for middleware internals: API detection, custom handlers, debug overrides."""

from __future__ import annotations

import json

import pytest

from api_response_toolkit.django.middleware import (
    APIExceptionMiddleware,
    _is_api_request,
    _load_custom_handler,
)
from django.test import Client, override_settings  # type: ignore[import-not-found]


class _FakeRequest:
    def __init__(self, path="/api/users/", accept="", content_type=""):
        self.path = path
        self.META = {}
        if accept:
            self.META["HTTP_ACCEPT"] = accept
        if content_type:
            self.META["CONTENT_TYPE"] = content_type


def test_is_api_request_path_prefix():
    assert _is_api_request(_FakeRequest(path="/api/users/")) is True


def test_is_api_request_accept_header():
    assert _is_api_request(_FakeRequest(path="/x/", accept="application/json")) is True


def test_is_api_request_content_type():
    assert _is_api_request(_FakeRequest(path="/x/", content_type="application/json")) is True


def test_is_api_request_non_api():
    assert _is_api_request(_FakeRequest(path="/pages/about/", accept="text/html")) is False


def test_load_custom_handler_valid(tmp_path, monkeypatch):
    import sys
    import types

    module = types.ModuleType("custom_handler_mod")
    module.my_handler = lambda exc, cfg: None  # noqa: E731
    monkeypatch.setitem(sys.modules, "custom_handler_mod", module)
    handler = _load_custom_handler("custom_handler_mod.my_handler")
    assert callable(handler)


def test_load_custom_handler_invalid_path():
    with pytest.raises(ValueError):
        _load_custom_handler("no_dot_path")


def test_load_custom_handler_not_callable(tmp_path, monkeypatch):
    import sys
    import types

    module = types.ModuleType("custom_handler_mod2")
    module.not_callable = 42
    monkeypatch.setitem(sys.modules, "custom_handler_mod2", module)
    with pytest.raises(TypeError):
        _load_custom_handler("custom_handler_mod2.not_callable")


def test_custom_error_handler_takes_over():
    """A configured custom_error_handler can return its own response."""
    import sys
    import types

    from django.http import JsonResponse  # type: ignore[import-not-found]

    def custom_handler(exc, cfg):
        return JsonResponse({"custom": True}, status=418)

    module = types.ModuleType("custom_handler_mod3")
    module.handler = custom_handler
    sys.modules["custom_handler_mod3"] = module

    client = Client(raise_request_exception=False)
    with override_settings(
        API_RESPONSE_TOOLKIT={"custom_error_handler": "custom_handler_mod3.handler"}
    ):
        resp = client.get("/plain/unhandled/")
    assert resp.status_code == 418
    assert json.loads(resp.content) == {"custom": True}

    sys.modules.pop("custom_handler_mod3", None)


def test_custom_error_handler_returns_none_falls_back():
    """If the custom handler returns None, the default builder is used."""
    import sys
    import types

    def custom_handler(exc, cfg):
        return None

    module = types.ModuleType("custom_handler_mod4")
    module.handler = custom_handler
    sys.modules["custom_handler_mod4"] = module

    client = Client(raise_request_exception=False)
    with override_settings(
        API_RESPONSE_TOOLKIT={"custom_error_handler": "custom_handler_mod4.handler"}
    ):
        resp = client.get("/plain/unhandled/")
    assert resp.status_code == 404
    body = json.loads(resp.content)
    assert body["code"] == "USER_NOT_FOUND"

    sys.modules.pop("custom_handler_mod4", None)


def test_middleware_debug_override():
    """middleware_debug override controls whether internal details are shown."""
    client = Client(raise_request_exception=False)
    with override_settings(
        API_RESPONSE_TOOLKIT={"middleware_debug": True}
    ):
        resp = client.get("/plain/unhandled/")
    # NotFoundError is an APIException, so its message is always preserved.
    body = json.loads(resp.content)
    assert body["message"] == "User not found"


def test_middleware_init_callable():
    """The middleware constructor stores get_response."""

    def get_response(request):
        return None

    mw = APIExceptionMiddleware(get_response)
    assert mw.get_response is get_response
