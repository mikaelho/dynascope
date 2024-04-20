import copy
import inspect
from contextlib import contextmanager
from typing import TypeVar

from dynascope.manager import Manager
from dynascope.manager import is_dynamic
from dynascope.wrappers import add_tracking_wrapper
from dynascope.wrappers import wrap_target


__all__ = "dynamic", "is_dynamic", "fix", "scope"


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
def scope_manager(obj, **kwargs):
    if not is_dynamic(obj):
        raise TypeError(f"{obj} is not dynamic")

    frame = inspect.currentframe().f_back.f_back
    previous_scopes = frame.f_locals.setdefault(obj._manager.locals_key, [])
    start_of_block_scope_length = len(previous_scopes)
    for key, value in kwargs.items():
        obj._manager.mutate(frame, obj._path, "__setattr__", (key, value), {})

    yield

    frame.f_locals[obj._manager.locals_key] = previous_scopes[:start_of_block_scope_length]


class Scope:
    """Empty object container."""
    pass


scope = dynamic(Scope)


# class Scope:
#     # def __new__(cls, *args, **kwargs):
#     #     self = super().__new__(cls, *args, **kwargs)
#     #     return dynamic(self)
#
#     @contextmanager
#     def __call__(self, manager, path, **kwargs):
#         frame = inspect.currentframe().f_back.f_back
#         previous_scopes = frame.f_locals.setdefault(manager.locals_key, [])
#         start_of_block_scope_length = len(previous_scopes)
#         for key, value in kwargs.items():
#             manager.mutate(frame, path, "__setattr__", (key, value), {})
#
#         yield
#
#         frame.f_locals[manager.locals_key] = previous_scopes[:start_of_block_scope_length]
#
#
# scopish = dynamic(Scope())


class Static:
    """
    Container that remains static when placed in a dynamic object.
    """
    def __init__(self, value=None):
        self.value = value

    def __deepcopy__(self, memo):
        return self
