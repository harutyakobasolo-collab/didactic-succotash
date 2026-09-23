import httpx
import pytest

from sdetflow.errors import ExtractionError
from sdetflow.extract import extract_response, resolve_path


def response(json_value, status=200):
    return httpx.Response(status, json=json_value, headers={"x-trace-id": "trace-1"})


def test_resolve_nested_json_and_list_index():
    data = {"data": {"items": [{"id": "p-1"}]}}
    assert resolve_path(data, "$.data.items[0].id") == "p-1"


def test_extract_status_header_and_body():
    res = response({"code": 0})
    assert extract_response(res, "status_code") == 200
    assert extract_response(res, "headers.x-trace-id") == "trace-1"
    assert extract_response(res, "$.code") == 0


def test_invalid_path_has_clear_error():
    with pytest.raises(ExtractionError, match="无法从路径"):
        resolve_path({"data": {}}, "$.data.missing")

