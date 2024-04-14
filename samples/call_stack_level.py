"Convenience functions to demonstrate dynamic scope behavior in a call stack."

from dynascope import scope
from dynascope import stack
from dynascope.manager import transparent


@transparent
def increment_level():
    "Convenience function to increase call stack level explicitly."
    stack.call_stack_level = getattr(stack, "call_stack_level", 0) + 1
    return stack.call_stack_level


def new_level():
    "Context manager to mark a new call stack level."
    current_level = getattr(stack, "call_stack_level", 0) + 1
    return scope(stack, call_stack_level=current_level)


def get_level():
    "Convenience function to get the current level."
    return getattr(stack, "call_stack_level", 0)
