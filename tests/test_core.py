from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from types import SimpleNamespace

import pytest

from dynascope import dynamic
from dynascope import fix
from dynascope import stack


def test_vanilla_scopes():

    global global_module_scope

    global_module_scope = 1

    def main():

        def func_child(local_scope=2):
            assert global_module_scope == 1
            assert local_scope == 2
            assert enclosing_scope == 3
            with pytest.raises(NameError):
                assert dynamic_scope == 4

        def func_parent():
            dynamic_scope = 4
            func_child()

        enclosing_scope = 3

        func_parent()

    main()


def test_dynamic_scope_added():

    global global_module_scope

    global_module_scope = 1

    def main():

        def func_child(local_scope=2):
            assert global_module_scope == 1
            assert local_scope == 2
            assert enclosing_scope == 3
            assert stack.dynamic_scope == 4

        def func_parent():
            stack.dynamic_scope = 4
            func_child()

        enclosing_scope = 3

        func_parent()

    main()



def test_dynamic_dict():
    dynamic_dict = dynamic({})
    assert isinstance(dynamic_dict, dict)
    assert dynamic_dict == {}
    assert dynamic_dict.__subject__ == {}

    dynamic_dict["a"] = 1
    assert dynamic_dict.__subject__ == {"a": 1}
    assert dynamic_dict["a"] == 1

    dynamic_dict["b"] = {"c": 3}

    def child():
        assert dynamic_dict["a"] == 1

        dynamic_dict["a"] = {"b": 2}
        dynamic_dict["b"]["c"] = 4

        assert dynamic_dict["a"]["b"] == 2
        assert dynamic_dict["a"] == {"b": 2}

        a = dynamic_dict["a"]
        assert a == {"b": 2}

        b = a["b"]
        c = int(a["b"])
        d = fix(a["b"])
        assert b == c == d == 2  # In this scope b looks the same as the "static" c and d

        return a, b, c, d

    a, b, c, d = child()

    assert dynamic_dict["a"] == 1
    assert dynamic_dict["b"]["c"] == 3

    assert a == 1
    with pytest.raises(AttributeError, match="'int' object has no attribute 'b'"):
        assert b == 2  # Trying to resolve a["b"] but in this scope a == 1
    assert c == 2
    assert d == 2


def test_dynamic_dataclass():
    @dataclass
    class ServerSettings:
        host: str = ""

    @dataclass
    class Configuration:
        setting_1: int = 1
        server_settings: ServerSettings = field(default_factory=ServerSettings)

    conf = dynamic(Configuration)  # Or dynamic(Configuration())
    assert isinstance(conf, Configuration)
    assert asdict(fix(conf)) == {"server_settings": {"host": ""}, "setting_1": 1}
    assert conf.setting_1 == 1

    def child():
        conf.setting_1 = 2
        conf.server_settings.host = "https://example.com"
        assert conf.setting_1 == 2
        assert isinstance(conf.server_settings, ServerSettings)
        assert conf.server_settings.host == "https://example.com"

        return conf.setting_1, conf.server_settings

    setting_1, server_settings = child()

    assert conf.setting_1 == setting_1 == 1
    assert server_settings.host == ""


def test_context_manager():
    def child():
        assert stack.dynamic_variable == 3
        stack.dynamic_variable = 4

        with stack():
            stack.dynamic_variable = 5
            assert stack.dynamic_variable == 5

            with stack():
                stack.dynamic_variable = 6
                assert stack.dynamic_variable == 6

            assert stack.dynamic_variable == 5

        assert stack.dynamic_variable == 4

    stack.dynamic_variable = 1

    with stack():
        stack.dynamic_variable = 2
        assert stack.dynamic_variable == 2

    assert stack.dynamic_variable == 1

    with stack():
        stack.dynamic_variable = 3
        child()
        assert stack.dynamic_variable == 3

    assert stack.dynamic_variable == 1

    with stack(dynamic_variable=7):
        assert stack.dynamic_variable == 7

    assert stack.dynamic_variable == 1

    stack.next_level = SimpleNamespace(other_variable=1)

    with stack.next_level(other_variable=2):
        assert stack.next_level.other_variable == 2

    assert stack.next_level.other_variable == 1
