# -*- coding: utf-8 -*-

"""
This module implements the Log representation and utilities to work with it.

:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from typing import List, Dict, Union, Optional, cast
from .rsf.parser import Command, Action
from .exceptions import OrphanEntry, InsertException
from .blob import Blob
from .hash import Hash
from .record import Record
from .entry import Entry, Scope


class Log:
    """
    Represents a log of entries.
    """

    def __init__(self, entries: List[Entry] = None,
                 blobs: Dict[Hash, Blob] = None):
        self._entries = entries or []
        self._blobs = blobs or {}
        self._size = len(self._entries)

    @property
    def blobs(self) -> Dict[Hash, Blob]:
        """
        The set of blobs.
        """
        return self._blobs

    @property
    def entries(self) -> List[Entry]:
        """
        The list of entries.
        """
        return self._entries

    @property
    def size(self) -> int:
        """
        The size of the log.
        """
        return self._size

    def is_empty(self) -> bool:
        """Checks if the log is empty"""
        return self._size == 0

    def snapshot(self, size: int = None) -> Dict[str, Record]:
        """
        Collects the state of the log at the given size
        """

        records = {}

        for entry in self._entries[:size]:
            records[entry.key] = Record(entry, self._blobs[entry.blob_hash])

        return records

    def trail(self, key: str, size: int = None) -> List[Entry]:
        """
        Collects the trail of changes for the given key.
        """
        return [entry for entry in self._entries[:size] if entry.key == key]

    def stats(self):
        """
        Collects statistics from the log.
        """
        return {
            "total-entries": self._size,
            "total-blobs": len(self._blobs)
        }

    def insert(self, obj: Union[Entry, Blob, Hash]):
        """
        Inserts either a blob or an entry to the log.
        """

        if isinstance(obj, Entry):
            self._size = self.size + 1
            obj.set_position(self._size)
            self._entries.append(obj)

        elif isinstance(obj, Blob):
            self._blobs[obj.digest()] = obj

        else:
            msg = "Attempted to insert an unknown object of type {}".format(type(obj)) # NOQA
            raise InsertException(msg)

    def find(self, key: str) -> Optional[Record]:
        """
        Finds the latest blob for the given key.
        """

        return self.snapshot().get(key)


def collect(commands: List[Command],
            log: Optional[Log] = None,
            metalog: Optional[Log] = None) -> Dict[str, Log]:
    """
    Collects blobs, entries and computes records and schema (?)
    """
    data = log or Log()
    metadata = metalog or Log()
    blobs = {**data.blobs, **metadata.blobs}

    for command in commands:
        if command.action == Action.AssertRootHash:
            # Ignore assert commands until we have a way to check their
            # consistency.
            continue

        elif command.action == Action.AddItem:
            blobs[command.value.digest()] = cast(Blob, command.value)

        elif command.action == Action.AppendEntry:
            if command.value.scope == Scope.System:  # type: ignore
                metadata.insert(command.value)

            else:
                data.insert(command.value)

    for entry in data.entries:
        blob = blobs.get(entry.blob_hash)

        if blob is None:
            raise OrphanEntry(entry)

        data.insert(blob)

    for entry in metadata.entries:
        blob = blobs.get(entry.blob_hash)

        if blob is None:
            raise OrphanEntry(entry)

        metadata.insert(blob)

    return {"data": data, "metadata": metadata}


def slice(log: Log, start_position: int) -> List[Command]:
    """
    Slices the log as a list of commands.
    """

    commands = []

    for entry in log.entries[start_position:]:
        commands.append(Command(Action.AddItem, log.blobs[entry.blob_hash]))
        commands.append(Command(Action.AppendEntry, entry))

    return commands
