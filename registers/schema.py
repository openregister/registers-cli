"""
Schema implementation
"""
from typing import List
from enum import Enum
from .exceptions import AttributeAlreadyExists
from .blob import Blob


class Cardinality(Enum):
    One = "1"
    Many = "n"


class Datatype(Enum):
    Curie = "curie"
    Datetime = "datetime"
    Name = "name"
    Hash = "hash"
    Integer = "integer"
    Period = "period"
    String = "string"
    Text = "text"
    Timestamp = "timestamp"
    Url = "url"


class Attribute:
    """
    Schema attribute representation.

    TODO: text, phase, start_date, register, ...
    """
    def __init__(self, uid: str, datatype: Datatype, cardinality: Cardinality,
                 description: str = None):
        self._uid = uid
        self._datatype = datatype
        self._cardinality = cardinality
        self._description = description

    @property
    def uid(self) -> str:
        """The attribute unique identifier"""

        return self._uid

    @property
    def datatype(self) -> Datatype:
        """The attribute datatype"""

        return self._datatype

    @property
    def cardinality(self) -> Cardinality:
        """The attribute cardinality"""

        return self._cardinality


def attribute(blob: Blob) -> Attribute:
    """
    Attempts to transform the given blob to an Attribute.
    """
    uid = blob.get("field")
    datatype = Datatype(blob.get("datatype"))
    cardinality = Cardinality(blob.get("cardinality"))
    description = blob.get("text")

    return Attribute(uid, datatype, cardinality, description)


class Schema:
    """
    Schema representation. A set of attributes where one is the primary key.
    """
    def __init__(self, primary_key_id: str, attrs: List[Attribute] = None):
        self._primary_key = primary_key_id
        self._attrs = attrs or []

    @property
    def attributes(self):
        """
        The schema attributes
        """
        return self._attrs

    @property
    def primary_key(self):
        """
        The schema primary key (i.e. the primary attribute id)
        """
        return self._primary_key

    def insert(self, attr: Attribute):
        """
        Inserts a new attribute to the schema.
        """

        if attr.uid in [at.uid for at in self._attrs]:
            raise AttributeAlreadyExists(attr)

        self._attrs.append(attr)

    def get(self, uid):
        """
        Gets the attribute for the given identifier.
        """
        for attr in self._attrs:
            if attr.uid == uid:
                return attr

        return None
