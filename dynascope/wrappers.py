import copy
import inspect
from contextlib import contextmanager
from functools import partial
from typing import MutableMapping
from typing import MutableSequence
from typing import MutableSet
from typing import TypeVar

from peak.util.proxies import CallbackWrapper


T = TypeVar('T')


class DynamicObject(CallbackWrapper):

    def __init__(self, path, manager, osa=object.__setattr__):
        super().__init__(partial(manager.get_subject, path))

        osa(self, '_path', path)  # noqa
        osa(self, '_manager', manager)  # noqa

    @contextmanager
    def __call__(self, **kwargs):
        frame = inspect.currentframe().f_back.f_back
        previous_scopes = frame.f_locals.setdefault(self._manager.locals_key, [])
        start_of_block_scope_length = len(previous_scopes)
        for key, value in kwargs.items():
            self._manager.mutate(frame, self._path, "__setattr__", (key, value), {})

        yield

        frame.f_locals[self._manager.locals_key] = previous_scopes[:start_of_block_scope_length]

    def __repr__(self):
        return self.__subject__.__repr__()

    def __deepcopy__(self, memo):
        return copy.deepcopy(self.__subject__, memo)  # noqa

    def __getattribute__(self, attr, oga=object.__getattribute__):
        subject = oga(self, "__subject__")
        if attr == "__subject__":
            return subject
        elif attr in ("_path", "_manager"):
            return oga(self, attr)
        elif attr.startswith("_"):
            return getattr(subject, attr)
        else:
            return wrap_target(getattr(subject, attr), self._path + [attr], self._manager)

    def __getitem__(self, arg):
        return wrap_target(self.__subject__[arg], self._path + [arg], self._manager)


set_callback = DynamicObject.__callback__.__set__
get_callback = DynamicObject.__callback__.__get__
DynamicObject.__subject__ = property(lambda self, gc=get_callback: gc(self)(inspect.currentframe().f_back))


class DynamicMapping(DynamicObject):
    """
    Wrapper for MutableMappings.
    """


class DynamicSequence(DynamicObject):
    """
    Wrapper for MutableSequences.
    """


class DynamicSet(DynamicObject):
    """
    Wrapper for MutableSets.
    """


class DynamicCustomObject(DynamicObject):
    """ If an object has a __dict__ attribute, we track attribute changes. """


dynamic_types = {
    MutableSequence: DynamicSequence,
    MutableMapping: DynamicMapping,
    MutableSet: DynamicSet,
}

mutating_methods = {
    DynamicObject: [
        '__setattr__', '__delattr__',  # '__iadd__', '__isub__', '__imul__', '__imatmul__', '__itruediv__',
        # '__ifloordiv__', '__imod__', '__ipow__', '__ilshift__', '__irshift__', '__iand__', '__ixor__', '__ior__',
    ],
    DynamicMapping: [
        '__setitem__', '__delitem__', 'pop', 'popitem', 'clear', 'update', 'setdefault',
    ],
    DynamicSequence: [
        '__setitem__', '__delitem__', 'insert', 'append', 'reverse', 'extend', 'pop', 'remove', 'clear', '__iadd__',
    ],
    DynamicSet: [
        'add', 'discard', 'clear', 'pop', 'remove', '__ior__', '__iand__', '__ixor__', '__isub__',
    ],
}

# Add tracking wrappers to all mutating functions.

for dynamic_type in mutating_methods:
    for func_name in mutating_methods[dynamic_type]:
        def func(self, *args, tracker_function_name=func_name, **kwargs):
            result = self._manager.mutate(
                inspect.currentframe().f_back,
                self._path,
                tracker_function_name,
                args,
                kwargs,
            )
            return result

        setattr(dynamic_type, func_name, func)
        getattr(dynamic_type, func_name).__name__ = func_name


def wrap_target(target: T, path: list, manager: "Manager") -> T:
    for abc, wrapper in dynamic_types.items():
        if isinstance(target, abc):
            return wrapper(path, manager)
    return DynamicObject(path, manager)
