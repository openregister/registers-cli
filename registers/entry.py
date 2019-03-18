from typing import Optional
from enum import Enum
from hashlib import sha256
import json
from .hash import Hash
from .exceptions import MissingEntryKey


class Scope(Enum):
    User = 'user'
    System = 'system'


class Entry:
    """
    Represent an entry in the `Log` of changes.


    TODO:
    * entry validation
    * validate key
    * validate timestamp
    * validate blob exists
    * validate previous entry for key has a different blob -- (out of scope)
    """
    def __init__(self, key: str, scope: Scope, timestamp: str,
                 blob_hash: Hash, position: int = None):
        if not isinstance(key, str):
            raise MissingEntryKey()

        self._key = key
        self._scope = scope
        self._timestamp = timestamp
        self._blob_hash = blob_hash
        self._position = position

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
        The entry json representation
        """

        return json.dumps([self.to_dict()], separators=(',', ':'),
                          ensure_ascii=False)

    def to_dict(self):
        return {
            "index-entry-number": str(self._position),
            "entry-number": str(self._position),
            "entry-timestamp": self._timestamp,
            "key": self._key,
            "item-hash": [str(self._blob_hash)]
        }

    def set_position(self, number: int):
        self._position = number

    @property
    def position(self) -> Optional[int]:
        return self._position

    @property
    def key(self) -> str:
        return self._key

    @property
    def scope(self) -> Scope:
        return self._scope

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def blob_hash(self) -> Hash:
        return self._blob_hash
