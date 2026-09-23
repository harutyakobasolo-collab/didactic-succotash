import pytest

from sdetflow.errors import RenderError
from sdetflow.template import render


def test_render_preserves_native_type_for_full_placeholder():
    assert render("${quantity}", {"quantity": 2}) == 2


def test_render_nested_objects_and_embedded_values():
    value = {"headers": ["Bearer ${token}"], "user": "${profile}"}
    context = {"token": "abc", "profile": {"name": "Sun"}}
    assert render(value, context) == {"headers": ["Bearer abc"], "user": {"name": "Sun"}}


def test_render_supports_dot_path():
    assert render("hello ${user.name}", {"user": {"name": "tester"}}) == "hello tester"


def test_render_rejects_unknown_variable():
    with pytest.raises(RenderError, match="变量未定义"):
        render("${missing}", {})

