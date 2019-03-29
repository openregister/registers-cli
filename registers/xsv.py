# -*- coding: utf-8 -*-

"""
This module implements the functions to serialise and deserialise XSV
(Character Separated Values) typically comma ``,`` or tab ``\t``.

Multivalues have the delimiter semi-colon ``;`` and it can't be changed.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from typing import List, NewType, Dict, cast, Optional
import csv
from io import StringIO
from .blob import Blob, Value
from .entry import Entry
from .record import Record
from .schema import Cardinality, Schema
from .exceptions import RegistersException, UnknownAttribute, InvalidKey
from .validator import validate, validate_key


Row = NewType("Row", List[str])


def serialise(stream: StringIO, obj, headers: List[str]):
    """
    Serialises the given object to CSV.
    """

    writer = csv.writer(stream)
    writer.writerow(headers)

    if isinstance(obj, List):
        for element in obj:
            row = serialise_object(element, headers=headers)
            writer.writerow(row)

    elif isinstance(obj, Dict):
        for element in obj.values():
            row = serialise_object(element, headers=headers)
            writer.writerow(row)

    else:
        row = serialise_object(obj, headers=headers)
        writer.writerow(row)


def serialise_object(obj, headers: List[str] = None) -> Row:
    """
    Builds a row from the given object and headers.

    >>> from . import Hash, Scope, Entry, Blob, Record
    >>> blob = Blob({"foo": "abc", "bar": "xyz"})
    >>> serialise_object(blob, ["foo", "bar"])
    ['abc', 'xyz']

    >>> blob_hash = blob.digest()
    >>> entry = Entry("A", Scope.User, "2019-03-19T10:11:12Z", blob_hash, 1)
    >>> serialise_object(entry)
    ['1', '1', '2019-03-19T10:11:12Z', 'A', \
'sha-256:5dd4fe3b0de91882dae86b223ca531b5c8f2335d9ee3fd0ab18dfdc2871d0c61']

    >>> serialise_object(Record(entry, blob), ["foo", "bar"])
    ['1', '1', '2019-03-19T10:11:12Z', 'A', 'abc', 'xyz']
    """

    if isinstance(obj, Blob):
        if headers is None:
            raise RegistersException("In order to serialise a blob as a \
csv row you must pass the expected list of headers.")

        return cast(Row, [obj.get(header) for header in headers])

    if isinstance(obj, Entry):
        return cast(Row, [str(obj.position),
                          str(obj.position),
                          obj.timestamp,
                          obj.key,
                          str(obj.blob_hash)])

    if isinstance(obj, Record):
        if headers is None:
            raise RegistersException("In order to serialise a record as a \
csv row you must pass the expected list of headers for the blob.")

        headers = [header for header in headers
                   if header not in Entry.headers()]

        result = serialise_object(obj.entry)[:-1]
        result.extend(serialise_object(obj.blob, headers))

        return cast(Row, result)

    raise ValueError("Unknown type of object.")


def serialise_value(value: Value) -> str:
    """
    Serialises value and multivalue to a xsv representation.

    >>> serialise_value("foo")
    'foo'

    >>> serialise_value(["foo"])
    'foo'

    >>> serialise_value(["foo", "bar"])
    'foo;bar'

    >>> serialise_value(["foo", "bar;qux"])
    'foo;"bar;qux"'
    """

    if isinstance(value, List):
        return ";".join([quote_value(v) for v in value])

    return value


def quote_value(value: str) -> str:
    """
    Ensures values with ";" are quoted.

    >>> quote_value("foo")
    'foo'

    >>> quote_value("foo;bar")
    '"foo;bar"'
    """

    if value.find(";") != -1:
        return f'"{value}"'

    return value


##############################################################################
# Deserialise
##############################################################################


def deserialise(buffer: StringIO, schema: Schema) -> List[Blob]:
    """
    Reads an XSV stream and returns a list of blobs coerced with the given
    schema.
    """

    dialect = csv.Sniffer().sniff(buffer.read(2048))
    buffer.seek(0)

    return [coerce(row, schema) for row
            in csv.DictReader(buffer, dialect=dialect)]


def deserialise_value(token: str, cardinality: Cardinality) -> Optional[Value]:
    """
    Deserialises values given a cardinality.

    >>> from . import Cardinality
    >>> deserialise_value("foo", Cardinality.One)
    'foo'

    >>> deserialise_value(" foo  ", Cardinality.One)
    'foo'

    >>> deserialise_value("foo", Cardinality.Many)
    ['foo']

    >>> deserialise_value("foo;bar", Cardinality.Many)
    ['foo', 'bar']

    >>> deserialise_value("foo; bar", Cardinality.Many)
    ['foo', 'bar']

    >>> deserialise_value("foo;;bar", Cardinality.Many)
    ['foo', 'bar']

    >>> deserialise_value("foo;", Cardinality.Many)
    ['foo']

    >>> deserialise_value("", Cardinality.One) is None
    True

    >>> deserialise_value("", Cardinality.Many) is None
    True
    """

    if token is None or token.strip() == "":
        return None

    if cardinality == Cardinality.Many:
        return [value.strip() for value in split_token(token)
                if value.strip() != ""]

    return token.strip()


def split_token(token: str) -> List[str]:
    """
    Splits tokens separated by ";".

    If the resulting values have semicolons, the values must be quoted.

    >>> split_token('"foo";"bar;far"')
    ['foo', 'bar;far']
    """
    stream = csv.reader(StringIO(token), delimiter=";")

    return next(stream)


def coerce(data: Dict[str, str], schema: Schema) -> Blob:
    """
    Takes a dictionary and attempts to coerce it as a Blob and validate
    against the given Schema.

    >>> from . import Blob, Schema, schema
    >>> attrs = [schema.string("foo"), schema.integer_set("xs")]
    >>> schema = Schema("foo", attrs)

    >>> data = {"foo": "abc", "xs": None}
    >>> blob = Blob({"foo": "abc"})
    >>> coerce(data, schema) == blob
    True

    >>> data = {"foo": "abc", "xs": "1;2;3"}
    >>> blob = Blob({"foo": "abc", "xs": ["1", "2", "3"]})
    >>> coerce(data, schema) == blob
    True

    >>> data = {"foo": "abc"}
    >>> blob = Blob({"foo": "abc"})
    >>> coerce(data, schema) == blob
    True

    >>> data = {"foo": "abc", "xs": ""}
    >>> blob = Blob({"foo": "abc"})
    >>> coerce(data, schema) == blob
    True

    >>> data = {"foo": "abc", "xs": "1;"}
    >>> blob = Blob({"foo": "abc", "xs": ["1"]})
    >>> coerce(data, schema) == blob
    True

    >>> data = {"foo": "abc", "xs": ";"}
    >>> blob = Blob({"foo": "abc"})
    >>> coerce(data, schema) == blob
    True
    """

    clean_data = {}

    for key, value in data.items():
        if value is None or value.strip() in ["", ";"]:
            continue

        key = key.strip()
        attr = schema.get(key)

        if attr is None:
            raise UnknownAttribute(key, value)

        if key == schema.primary_key and not validate_key(value):
            raise InvalidKey(value)

        clean_data[key] = cast(Value, deserialise_value(value,
                                                        attr.cardinality))

    validate(clean_data, schema)

    return Blob(clean_data)
