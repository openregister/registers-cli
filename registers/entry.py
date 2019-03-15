from enum import Enum
from hashlib import sha256
import json


class Scope(Enum):
    User = 'user'
    System = 'system'


class Entry:
    def __init__(self, key, scope, timestamp, blob_hash):
        self._key = key
        self._scope = scope
        self._timestamp = timestamp
        self._blob_hash = blob_hash

    def __eq__(self, other):
        return self.digest() == other.digest()

    def __hash__(self):
        return self.digest()

    def __repr__(self):
        return self.to_json()

    def digest(self):
        """
        The digest of the Entry. V1 has undefined behaviour for this.
        """

        return sha256(self.to_json().encode('utf-8')).hexdigest()

    def to_json(self):
        """
        TODO: Needs to change to mimic ORJ to compute Merkle hashes.
        """

        data = {
            # "entry-number": entry_number,
            # "index-entry-number": entry_number,
            "key": self._key,
            "timestamp": self._timestamp,
            "item-hash": [str(self._blob_hash)]
        }

        return json.dumps(data, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False)

    @property
    def key(self):
        return self._key

    @property
    def scope(self):
        return self._scope

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def blob_hash(self):
        return self._blob_hash
