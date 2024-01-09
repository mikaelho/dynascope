import copy
import inspect
from contextlib import contextmanager
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


@contextmanager
def scope(obj, **kwargs):
    if not is_dynamic(obj):
        raise TypeError(f"{obj} is not dynamic")

    frame = inspect.currentframe().f_back.f_back
    previous_scopes = frame.f_locals.setdefault(obj._manager.locals_key, [])
    start_of_block_scope_length = len(previous_scopes)
    for key, value in kwargs.items():
        obj._manager.mutate(frame, obj._path, "__setattr__", (key, value), {})

    yield

    frame.f_locals[obj._manager.locals_key] = previous_scopes[:start_of_block_scope_length]


class Stack:
    """Empty object container."""
    pass


stack = dynamic(Stack)
