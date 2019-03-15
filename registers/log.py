"""
The log representation and utilities.
"""

from typing import List, Dict, Union
from .rsf.parser import Command, Action
from .exceptions import OrphanEntry, InsertException
from .blob import Blob
from .entry import Entry, Scope


class Log:
    """
    Represents a log of entries.
    """

    def __init__(self, entries: List[Entry] = None,
                 blobs: Dict[str, Blob] = None):
        self._entries = entries or []
        self._blobs = blobs or {}

    @property
    def blobs(self):
        """
        The set of blobs.
        """
        return self._blobs

    @property
    def entries(self):
        """
        The list of entries.
        """
        return self._entries

    def size(self):
        """
        The size of the log.
        """
        return len(self._entries)

    def snapshot(self, size: int = None):
        """
        Collects the state of the log at the given size
        """

        records = {}

        for entry in self._entries[:size]:
            records[entry.key] = self._blobs[entry.blob_hash.digest]

        return records

    def stats(self):
        """
        Collects statistics from the log.
        """
        return {
            "total-entries": len(self._entries),
            "total-blobs": len(self._blobs)
        }

    def insert(self, obj: Union[Entry, Blob]):
        """
        Inserts either a blob or an entry to the log.
        """

        if isinstance(obj, Entry):
            self._entries.append(obj)

        elif isinstance(obj, Blob):
            self._blobs[obj.digest] = obj

        else:
            msg = "Attempted to insert an unknown object of type {}".format(type(obj)) # NOQA
            raise InsertException(msg)

    def find(self, key: str) -> Blob:
        """
        Finds the latest blob for the given key.
        """

        return self.snapshot().get(key)


def collect(commands: List[Command]) -> Dict[str, Log]:
    """
    Collects blobs, entries and computes records and schema (?)
    """
    blobs = {}
    data = Log()
    metadata = Log()

    for command in commands:
        if command.action == Action.AssertRootHash:
            # Ignore assert commands until we have a way to check their
            # consistency.
            pass

        elif command.action == Action.AddItem:
            blobs[command.value.digest] = command.value

        elif command.action == Action.AppendEntry:
            if command.value.scope == Scope.System:
                metadata.insert(command.value)

            else:
                data.insert(command.value)

    for entry in data.entries:
        blob = blobs.get(entry.blob_hash.digest)

        if blob is None:
            raise OrphanEntry(entry)

        data.insert(blob)

    for entry in metadata.entries:
        blob = blobs.get(entry.blob_hash.digest)

        if blob is None:
            raise OrphanEntry(entry)

        metadata.insert(blob)

    return {"data": data, "metadata": metadata}
