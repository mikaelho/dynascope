"Convenience functions to demonstrate dynamic scope behavior in a call stack."

from dynascope import scope_manager
from dynascope import scope
from dynascope.manager import transparent


@transparent
def increment_level():
    "Convenience function to increase call stack level explicitly."
    scope.call_stack_level = getattr(scope, "call_stack_level", 0) + 1
    return scope.call_stack_level


def new_level():
    "Context manager to mark a new call stack level."
    current_level = getattr(scope, "call_stack_level", 0) + 1
    return scope_manager(scope, call_stack_level=current_level)


def get_level():
    "Convenience function to get the current level."
    return getattr(scope, "call_stack_level", 0)
