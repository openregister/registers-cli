from typing import Dict, Union, List, Optional
from hashlib import sha256
import json
from .hash import Hash


Value = Union[str, List[str]]


class Blob:
    """
    Represents a blob of data (i.e. an 'item' in V1 parlance).
    """

    def __init__(self, data: Dict[str, Value]):
        self._data = data

    def __hash__(self):
        return self.digest()

    def __eq__(self, other):
        return self.digest() == other.digest()

    def __repr__(self):
        return self.to_json()

    def __iter__(self):
        self.__pairs = iter(sorted(self._data.items()))

        return self

    def __next__(self):
        return next(self.__pairs)

    def digest(self) -> Hash:
        """The digest of the Blob according to V1"""

        buffer = self.to_json().encode('utf-8')

        return Hash("sha-256", sha256(buffer).hexdigest())

    def to_json(self) -> str:
        """
        Canonicalises according to the Registers Specification V1:
        https://spec.openregister.org/v1/glossary/item#canonicalisation
        """

        return json.dumps(self._data, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False)

    def to_dict(self) -> Dict[str, Union[str, List[str]]]:
        return {k: v for k, v in sorted(self._data.items())}

    def get(self, key: str) -> Optional[Value]:
        """
        Attempts to get the value for the given key.
        """
        return self._data.get(key)
