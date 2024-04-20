import pytest

from dynascope import scope_manager
from dynascope import scope


def test_example_1():
    scope.variable = 1

    def function():
        assert scope.variable == 1
        scope.variable = 2
        assert scope.variable == 2

    function()
    assert scope.variable == 1


def test_example_2():
    scope.variable = 1

    with scope():
        assert scope.variable == 1
        scope.variable = 2
        assert scope.variable == 2

    assert scope.variable == 1


def test_example_3():
    scope.variable = 1

    with scope(variable=2):
        assert scope.variable == 2

    assert scope.variable == 1


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
            assert scope.dynamic_scope == 4

        def func_parent():
            scope.dynamic_scope = 4
            func_child()

        enclosing_scope = 3

        func_parent()

    main()
