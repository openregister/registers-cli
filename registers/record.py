# -*- coding: utf-8 -*-

"""
This module implements the Record representation.

:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from typing import Optional, Any, Dict
import json
from . import Entry, Blob, Value
from .exceptions import InconsistentRecord


class Record:
    """
    Represents a record.
    """

    def __init__(self, entry: Entry, blob: Blob):
        if entry.blob_hash != blob.digest():
            raise InconsistentRecord((entry.key, entry.blob_hash))

        self._entry = entry
        self._blob = blob

    def __eq__(self, other):
        return (self._entry, self._blob) == (other.entry, other.blob)

    def __repr__(self):
        return self.to_json()

    def to_json(self) -> str:
        """
        JSON representation as specified by V1
        """

        return json.dumps({self._entry.key: self.to_dict()},
                          separators=(',', ':'),
                          ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns the record data as a dictionary.
        """

        data = self._entry.to_dict()
        del data["item-hash"]
        data["item"] = [self._blob.to_dict()]

        return data

    @property
    def entry(self) -> Entry:
        """
        The record entry.
        """

        return self._entry

    @property
    def blob(self) -> Blob:
        """
        The record blob.
        """

        return self._blob

    def get(self, key: str) -> Optional[Value]:
        """
        Attempts to get the value for the given key.
        """

        return self._blob.get(key)
