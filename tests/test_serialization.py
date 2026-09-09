"""Tests for JSON serialization of common Python values."""

from __future__ import annotations

import datetime
import json

from api_response_toolkit import success, to_dict


def _serialize(payload):
    """Serialize a payload to a JSON string (exercising stdlib json)."""
    return json.dumps(to_dict(payload), default=str)


def test_serialize_dict():
    body = _serialize(success(data={"a": 1}))
    assert json.loads(body)["data"] == {"a": 1}


def test_serialize_list():
    body = _serialize(success(data=[1, 2, 3]))
    assert json.loads(body)["data"] == [1, 2, 3]


def test_serialize_tuple():
    body = _serialize(success(data=(1, 2, 3)))
    assert json.loads(body)["data"] == [1, 2, 3]


def test_serialize_string():
    body = _serialize(success(data="hello"))
    assert json.loads(body)["data"] == "hello"


def test_serialize_int():
    body = _serialize(success(data=42))
    assert json.loads(body)["data"] == 42


def test_serialize_float():
    body = _serialize(success(data=3.14))
    assert json.loads(body)["data"] == 3.14


def test_serialize_bool():
    body = _serialize(success(data=True))
    assert json.loads(body)["data"] is True


def test_serialize_none_data():
    body = _serialize(success(data=None))
    # data omitted by default
    assert "data" not in json.loads(body)


def test_serialize_datetime_via_default():
    dt = datetime.datetime(2024, 1, 1, 12, 0, 0)
    body = _serialize(success(data=dt))
    assert json.loads(body)["data"] == "2024-01-01 12:00:00"


def test_serialize_nested_structure():
    data = {
        "user": {"id": 1, "tags": ["a", "b"], "active": True},
        "count": 10,
    }
    body = _serialize(success(data=data))
    assert json.loads(body)["data"] == data


def test_to_dict_returns_json_serializable_for_basic_types():
    body = to_dict(success(data={"k": [1, True, None, "x"]}))
    # Should not raise
    json.dumps(body)
