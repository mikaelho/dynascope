from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from types import SimpleNamespace

import pytest

from dynascope import Static
from dynascope import dynamic
from dynascope import fix
from dynascope import scope_manager
from dynascope import scope


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
    class PluginSettings:
        name: str = ""

    @dataclass
    class Configuration:
        setting_1: int = 1
        server_settings: ServerSettings = field(default_factory=ServerSettings)
        plugins: list[PluginSettings] = field(default_factory=list)

    conf = dynamic(Configuration)  # Or dynamic(Configuration())
    assert isinstance(conf, Configuration)
    assert asdict(fix(conf)) == {"setting_1": 1, "server_settings": {"host": ""}, "plugins": []}
    assert conf.setting_1 == 1

    def child():
        conf.setting_1 = 2
        conf.server_settings.host = "https://example.com"
        conf.plugins.append(PluginSettings("secure"))
        assert conf.setting_1 == 2
        assert isinstance(conf.server_settings, ServerSettings)
        assert conf.server_settings.host == "https://example.com"
        plugin = conf.plugins[0]
        assert isinstance(plugin, PluginSettings)
        assert plugin.name == "secure"

        with scope_manager(plugin):
            plugin.name = "unsecure"
            assert plugin.name == "unsecure"

        assert plugin.name == "secure"

        return conf.setting_1, conf.server_settings, conf.plugins

    setting_1, server_settings, plugins = child()

    assert conf.setting_1 == setting_1 == 1
    assert server_settings.host == ""
    assert plugins == []


# def test_scopish():
#     scopish.variable = 1
#
#     def function():
#         assert scopish.variable == 1
#         scopish.variable = 2
#         assert scopish.variable == 2
#
#     function()
#     assert scopish.variable == 1
#
#
# def test_scopish_context_manager():
#     scopish.variable = 1
#
#     with scopish():
#         assert scopish.variable == 1
#         scopish.variable = 2
#         assert scopish.variable == 2
#
#     assert scopish.variable == 1


def test_context_manager():
    def child():
        assert scope.dynamic_variable == 3
        scope.dynamic_variable = 4

        with scope_manager(scope):
            scope.dynamic_variable = 5
            assert scope.dynamic_variable == 5

            with scope_manager(scope):
                scope.dynamic_variable = 6
                assert scope.dynamic_variable == 6

            assert scope.dynamic_variable == 5

        assert scope.dynamic_variable == 4

    scope.dynamic_variable = 1

    with scope_manager(scope):
        scope.dynamic_variable = 2
        assert scope.dynamic_variable == 2

    assert scope.dynamic_variable == 1

    with scope_manager(scope):
        scope.dynamic_variable = 3
        child()
        assert scope.dynamic_variable == 3

    assert scope.dynamic_variable == 1

    with scope_manager(scope):
        scope.dynamic_variable = 7
        assert scope.dynamic_variable == 7

    assert scope.dynamic_variable == 1

    scope.next_level = SimpleNamespace(other_variable=1)

    with scope_manager(scope):
        scope.next_level.other_variable = 2
        assert scope.next_level.other_variable == 2

    assert scope.next_level.other_variable == 1


def test_carrying():
    load = Static({"value": 1})
    mule = dynamic({"load": load, "other": 2})

    with scope_manager(mule):
        mule["other"] = 3
        mule["load"].value["value"] = 2

    assert mule["other"] == 2
    assert mule["load"].value["value"] == load.value["value"] == 2


def test_dynamic_depth():
    @dataclass
    class Callstack:
        depth: int = 1

    callstack = dynamic(Callstack())

    with scope_manager(callstack):
        callstack.depth = callstack.depth + 1
        assert callstack.depth == 2

    assert callstack.depth == 1
