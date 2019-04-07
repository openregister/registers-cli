# -*- coding: utf-8 -*-

"""
This module implements the Log representation and utilities to work with it.

:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from typing import List, Dict, Union, Optional, cast, Tuple
from .rsf.parser import Command, Action
from .exceptions import (OrphanEntry, InsertException, DuplicatedEntry,
                         ValidationError, InconsistentLog)
from .blob import Blob
from .hash import Hash
from .record import Record
from .entry import Entry, Scope
from . import merkle


class Log:
    """
    Represents a log of entries.
    """

    def __init__(self, entries: List[Entry] = None,
                 blobs: Dict[Hash, Blob] = None):
        self._entries = entries or []
        self._blobs = blobs or {}
        self._size = len(self._entries)
        self._digest = merkle.Tree(self.byte_entries()).root_hash

    def __hash__(self):
        return self.digest()

    def __eq__(self, other):
        return self.digest() == other.digest()

    def digest(self) -> Hash:
        """
        The digest of the Log according to V1. Another name for the log digest
        is the "merkle root hash" which is used in the RSF command
        `assert-root-hash`.
        """

        return Hash("sha-256", self._digest.hex())

    def byte_entries(self):
        """
        The list of entries represented as bytes. Typically you want to use
        this as leaves for a merkle tree:

            from registers import merkle
            merkle.Tree(log.byte_entries)
        """

        return [entry.bytes() for entry in self._entries]

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

    def insert(self, obj: Union[Entry, Blob]):
        """
        Inserts either a blob or an entry to the log.
        """

        if isinstance(obj, Entry):
            self._size = self.size + 1
            obj.set_position(self._size)
            self._entries.append(obj)
            self._digest = merkle.Tree(self.byte_entries()).root_hash

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


def collect(commands: List[Command],  # pylint: disable=too-many-branches
            log: Optional[Log] = None,
            metalog: Optional[Log] = None,
            relaxed=False) -> Dict[str, object]:
    """
    Collects blobs, entries and computes records and schema (?)

    :param relaxed: If True it accepts duplicated entries. This param
                    ensures backwards compatibility with current registers.
                    For example, the country register has a duplicate entry
                    for `field:country`.
    """
    data = log or Log()
    metadata = metalog or Log()
    blobs = {**data.blobs, **metadata.blobs}
    errors = []

    for command in commands:
        if command.action == Action.AssertRootHash:
            digest = cast(Hash, command.value)

            if digest != data.digest():
                raise InconsistentLog(digest, data.digest(), data.size)

        elif command.action == Action.AddItem:
            blobs[command.value.digest()] = cast(Blob, command.value)

        elif command.action == Action.AppendEntry:
            entry = cast(Entry, command.value)
            blob = blobs.get(entry.blob_hash)

            if blob is None:
                raise OrphanEntry(entry)

            if entry.scope == Scope.System:
                metadata.insert(blob)
                record = metadata.snapshot().get(entry.key)
                (_, err) = _collect_entry(entry, record)

                if err and not relaxed:
                    errors.append(err)
                else:
                    metadata.insert(entry)
            else:
                data.insert(blob)
                record = data.snapshot().get(entry.key)
                (_, err) = _collect_entry(entry, record)

                if err and not relaxed:
                    errors.append(err)
                else:
                    data.insert(entry)

    return {"data": data, "metadata": metadata, "errors": errors}


def slice(log: Log, start_position: int) -> List[Command]:
    """
    Slices the log as a list of commands.
    """

    commands = []

    for entry in log.entries[start_position:]:
        commands.append(Command(Action.AddItem, log.blobs[entry.blob_hash]))
        commands.append(Command(Action.AppendEntry, entry))

    return commands


Result = Tuple[Optional[Entry], Optional[ValidationError]]


def _collect_entry(entry: Entry, record: Optional[Record]) -> Result:
    if record and record.blob.digest() == entry.blob_hash:
        return (None, DuplicatedEntry(entry.key, record.blob))

    return (entry, None)
