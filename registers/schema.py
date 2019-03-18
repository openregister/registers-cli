"""
Schema implementation
"""
from typing import List, Optional, cast
import json
from enum import Enum
from .exceptions import AttributeAlreadyExists, MissingAttributeIdentifier
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
                 description: Optional[str] = None):
        if not isinstance(uid, str):
            raise MissingAttributeIdentifier()

        self._uid = uid
        self._datatype = datatype
        self._cardinality = cardinality
        self._description = description

    def __eq__(self, other):
        return (self.uid == other.uid and
                self.datatype == other.datatype and
                self.cardinality == other.cardinality)

    def __repr__(self):
        return self.to_json()

    def __iter__(self):
        for item in self.to_dict().items():
            yield item

    def to_dict(self):
        data = {"field": self._uid,
                "datatype": repr(self._datatype.value),
                "cardinality": repr(self._cardinality.value)}

        if self._description:
            data["text"] = self._description

        return data

    def to_json(self):
        return json.dumps(dict(self), separators=(',', ':'),
                          ensure_ascii=False)

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
    uid = cast(str, blob.get("field"))
    datatype = Datatype(blob.get("datatype"))
    cardinality = Cardinality(blob.get("cardinality"))
    description = cast(Optional[str], blob.get("text"))

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

    def is_ready(self):
        """
        Checks if the schema is ready to be used.

        A schema is ready when it has a primary attribute and a non primary
        attribute.
        """
        return (len(self._attrs) > 1 and
                self.get(self._primary_key) is not None)

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


def string(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a string attribute.

    >>> attr = Attribute("foo", Datatype.String, Cardinality.One)
    >>> string("foo") == attr
    True
    """

    return Attribute(uid, Datatype.String, Cardinality.One)


def string_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a string set attribute.

    >>> attr = Attribute("foo", Datatype.String, Cardinality.Many)
    >>> string_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.String, Cardinality.Many)


def integer(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct an integer attribute.

    >>> attr = Attribute("foo", Datatype.Integer, Cardinality.One)
    >>> integer("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Integer, Cardinality.One)


def integer_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct an integer set attribute.

    >>> attr = Attribute("foo", Datatype.Integer, Cardinality.Many)
    >>> integer_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Integer, Cardinality.Many)


def curie(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a curie attribute.

    >>> attr = Attribute("foo", Datatype.Curie, Cardinality.One)
    >>> curie("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Curie, Cardinality.One)


def curie_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a curie attribute.

    >>> attr = Attribute("foo", Datatype.Curie, Cardinality.Many)
    >>> curie_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Curie, Cardinality.Many)


def datetime(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a datetime attribute.

    >>> attr = Attribute("foo", Datatype.Datetime, Cardinality.One)
    >>> datetime("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Datetime, Cardinality.One)


def datetime_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a datetime set attribute.

    >>> attr = Attribute("foo", Datatype.Datetime, Cardinality.Many)
    >>> datetime_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Datetime, Cardinality.Many)


def name(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a name attribute.

    >>> attr = Attribute("foo", Datatype.Name, Cardinality.One)
    >>> name("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Name, Cardinality.One)


def name_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a name set attribute.

    >>> attr = Attribute("foo", Datatype.Name, Cardinality.Many)
    >>> name_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Name, Cardinality.Many)


def hash(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a hash attribute.

    >>> attr = Attribute("foo", Datatype.Hash, Cardinality.One)
    >>> hash("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Hash, Cardinality.One)


def hash_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a hash set attribute.

    >>> attr = Attribute("foo", Datatype.Hash, Cardinality.Many)
    >>> hash_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Hash, Cardinality.Many)


def period(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct period attribute.

    >>> attr = Attribute("foo", Datatype.Period, Cardinality.One)
    >>> period("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Period, Cardinality.One)


def period_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a period set attribute.

    >>> attr = Attribute("foo", Datatype.Period, Cardinality.Many)
    >>> period_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Period, Cardinality.Many)


def text(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a text attribute.

    >>> attr = Attribute("foo", Datatype.Text, Cardinality.One)
    >>> text("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Text, Cardinality.One)


def text_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct text set attribute.

    >>> attr = Attribute("foo", Datatype.Text, Cardinality.Many)
    >>> text_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Text, Cardinality.Many)


def timestamp(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a timestamp attribute.

    >>> attr = Attribute("foo", Datatype.Timestamp, Cardinality.One)
    >>> timestamp("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Timestamp, Cardinality.One)


def timestamp_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a timestamp set attribute.

    >>> attr = Attribute("foo", Datatype.Timestamp, Cardinality.Many)
    >>> timestamp_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Timestamp, Cardinality.Many)


def url(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a url attribute.

    >>> attr = Attribute("foo", Datatype.Url, Cardinality.One)
    >>> url("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Url, Cardinality.One)


def url_set(uid: str, description: str = None) -> Attribute:
    """
    Helper function to construct a url set attribute.

    >>> attr = Attribute("foo", Datatype.Url, Cardinality.Many)
    >>> url_set("foo") == attr
    True
    """

    return Attribute(uid, Datatype.Url, Cardinality.Many)
