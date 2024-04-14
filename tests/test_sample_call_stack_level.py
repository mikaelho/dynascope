from samples.call_stack_level import get_level
from samples.call_stack_level import increment_level
from samples.call_stack_level import new_level


def test_sample_call_stack_level__function_calls():
    assert get_level() == 0

    def first():
        assert increment_level() == 1

        def second():
            assert increment_level() == 2

        second()

    first()

    assert get_level() == 0


def test_sample_call_stack_level__with_context_manager():
    assert get_level() == 0

    with new_level():
        assert get_level() == 1

        with new_level():
            assert get_level() == 2

        assert get_level() == 1

    assert get_level() == 0
