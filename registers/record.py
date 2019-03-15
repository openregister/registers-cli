import json
from . import Entry, Blob
from .exceptions import InconsistentRecord


class Record:
    """
    Represents a record.
    """
    def __init__(self, entry: Entry, blob: Blob):
        if entry.blob_hash.digest != blob.digest():
            raise InconsistentRecord((entry.key, entry.blob_hash.value))

        self._entry = entry
        self._blob = blob

    def __eq__(self, other):
        return (self._entry, self._blob) == (other.entry, other.blob)

    def __repr__(self):
        return self.to_json()

    def to_json(self):
        """
        JSON representation as specified by V1
        """

        data = self._entry.to_dict()
        del data["item-hash"]
        data["item"] = [self._blob.to_dict()]
        return json.dumps({self._entry.key: data}, separators=(',', ':'),
                          ensure_ascii=False)

    @property
    def entry(self):
        return self._entry

    @property
    def blob(self):
        return self._blob

    def get(self, key: str) -> str:
        return self._blob.get(key)
