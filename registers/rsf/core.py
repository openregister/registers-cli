# -*- coding: utf-8 -*-

"""
This module implements the RSF core represetations: Command and Action.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from typing import Union
from enum import Enum
from ..blob import Blob
from ..entry import Entry
from ..hash import Hash


Value = Union[Blob, Entry, Hash]


class Action(Enum):
    """
    Represents the RSF actions.
    """

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
        """
        The command action.
        """

        return self._action

    @property
    def value(self) -> Value:
        """
        The command value.
        """

        return self._value


def assert_root_hash(root_hash: Hash) -> Command:
    """
    Composes an assert root hash command.
    """

    return Command(Action.AssertRootHash, root_hash)


def add_item(blob: Blob) -> Command:
    """
    Composes an add item command.
    """

    return Command(Action.AddItem, blob)


def append_entry(entry: Entry) -> Command:
    """
    Composes an append entry command.
    """

    return Command(Action.AppendEntry, entry)
