import copy
from typing import TypeVar

from dynascope.manager import Manager
from dynascope.manager import is_dynamic
from dynascope.wrappers import wrap_target


__all__ = "dynamic", "is_dynamic", "fix", "stack"


T = TypeVar("T")


def dynamic(
    target: T,
) -> T:
    """
    Tag target data structure to get notified of any changes.

    Return value is a proxy type, but type hinted to match the tagged object for editor convenience.
    """
    if type(target) is type:
        target = target()

    manager = Manager(target)
    wrapped = wrap_target(target, [], manager)

    return wrapped


def fix(obj):
    if is_dynamic(obj):
        obj = obj.__subject__
    return copy.deepcopy(obj)


class Stack:
    """Empty object container."""
    pass


stack = dynamic(Stack)
