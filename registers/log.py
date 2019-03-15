"""
The log representation and utilities.
"""

from typing import List, Dict, Union
from .rsf.parser import Command, Action
from .exceptions import OrphanEntry, InsertException
from .blob import Blob
from .record import Record
from .entry import Entry, Scope


class Log:
    """
    Represents a log of entries.
    """

    def __init__(self, entries: List[Entry] = None,
                 blobs: Dict[str, Blob] = None):
        self._entries = entries or []
        self._blobs = blobs or {}
        self._size = len(self._entries)

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

    @property
    def size(self):
        """
        The size of the log.
        """
        return self._size

    def snapshot(self, size: int = None) -> Dict[str, Record]:
        """
        Collects the state of the log at the given size
        """

        records = {}

        for entry in self._entries[:size]:
            records[entry.key] = Record(entry,
                                        self._blobs[entry.blob_hash.digest])

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
            obj.position(self._size)
            self._entries.append(obj)

        elif isinstance(obj, Blob):
            self._blobs[obj.digest()] = obj

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
            blobs[command.value.digest()] = command.value

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
