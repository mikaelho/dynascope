import copy
from collections.abc import MutableMapping
from collections.abc import MutableSequence
from collections.abc import MutableSet
from typing import Any

from dynascope.wrappers import DynamicObject
from dynascope.wrappers import wrap_target


class Manager:

    def __init__(self, initial_value):
        self.initial_value = initial_value
        self.root_type = type(initial_value)

        self.start_of_block_scope_length = 0

    @property
    def locals_key(self):
        return f"_dynascope_{str(self.root_type)}"

    def get_subject(self, path, frame):
        root_value = self.get_from_stack(frame)
        return self.get_value_by_path(root_value, path)

    def get_plain_value(self, frame, path):
        root_value = self.get_from_stack(frame)
        return self.get_value_by_path(root_value, path)

    def get_value(self, frame, path):
        value = self.get_plain_value(frame, path)
        return wrap_target(value, path, self)

    def mutate(self, frame, path, function_name, args, kwargs):
        stack_value = self.get_from_stack(frame)
        new_value = copy.deepcopy(stack_value)
        value_for_mutation = self.get_value_by_path(new_value, path)
        result = getattr(value_for_mutation, function_name)(*args, **kwargs)
        self.add_to_stack(new_value, frame)
        return wrap_target(result, path, self)

    def add_to_stack(self, obj, frame):
        frame.f_locals.setdefault(self.locals_key, []).append(obj)

    def get_from_stack(self, frame) -> Any | None:
        while frame:
            previous_scopes = frame.f_locals.get(self.locals_key)
            if previous_scopes:
                return previous_scopes[-1]
            frame = frame.f_back

        return self.initial_value

    @staticmethod
    def get_value_by_path(obj, path: list):
        path = path.copy()

        while path:
            key = path.pop(0)
            if isinstance(obj, (MutableSequence, MutableMapping)):
                obj = obj[key]
            elif isinstance(obj, MutableSet):
                obj = key
            else:
                obj = object.__getattribute__(obj, key)
        return obj


def is_dynamic(obj):
    return isinstance(obj, DynamicObject)
