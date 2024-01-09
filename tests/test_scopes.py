import pytest

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
