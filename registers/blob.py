from hashlib import sha256
import json


class Blob:
    """
    Represents a blob of data (i.e. an 'item' in V1 parlance).
    """

    def __init__(self, data):
        self._data = data

    def __hash__(self):
        return self.digest()

    def __eq__(self, other):
        return self.digest() == other.digest()

    def __repr__(self):
        return self.to_json()

    def digest(self):
        """The digest of the Blob according to V1"""

        return sha256(self.to_json().encode('utf-8')).hexdigest()

    def to_json(self):
        """
        Canonicalises according to the Registers Specification V1:
        https://spec.openregister.org/v1/glossary/item#canonicalisation
        """

        return json.dumps(self._data, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False)

    def to_dict(self):
        return {k: v for k, v in sorted(self._data.items())}

    def get(self, key: str) -> str:
        """
        Attempts to get the value for the given key.
        """
        return self._data[key]


def coerce(data):
    """
    Takes a dictionary and attempts to coerce it as a Blob.
    """

    # trim spaces
    # discard empty values as nully.
    # validate PK exists -- schema
    # validate values -- schema
    # validate fields exist in the schema -- schema
    # validate card -- schema
    # validate card formatting (e.g. ;, do we allow spaces after ;?) -- schema
    # validate reference integrity -- (out of scope) schema, other registers
    # guard against equal blobs with different PK -- (out of scope) schema.

    # entry validation
    # validate key
    # validate timestamp
    # validate blob exists
    # validate previous entry for key has a different blob -- (out of scope)
    pass
