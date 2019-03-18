"""
RSF core types
"""

from typing import Union
from enum import Enum
from ..blob import Blob
from ..entry import Entry
from ..hash import Hash


Value = Union[Blob, Entry, Hash]


class Action(Enum):
    AddItem = 'add-item'
    AppendEntry = 'append-entry'
    AssertRootHash = 'assert-root-hash'


class Command:
    """
    Represents an RSF command
    """

    def __init__(self, action: Action, value: Value):
        self._action = action
        self._value = value

    def __eq__(self, other):
        return (self._action == other.action and
                self._value == other.value)

    def __repr__(self):
        tokens = []

        if isinstance(self._value, Blob):
            tokens = [self._action.value, self._value]

        if isinstance(self._value, Entry):
            tokens = [
                self._action.value,
                self._value.scope.value,
                self._value.key,
                self._value.timestamp,
                self._value.blob_hash
            ]

        if isinstance(self._value, Hash):
            tokens = [self._action.value, self._value]

        return "\t".join([str(x) for x in tokens])

    @property
    def action(self) -> Action:
        return self._action

    @property
    def value(self) -> Value:
        return self._value
