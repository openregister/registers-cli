import re
from typing import Dict, Union, List
from .schema import Schema, Cardinality, Datatype, Attribute
from .exceptions import (MissingPrimaryKey, CardinalityMismatch,
                         RepresentationError, UnknownAttribute,
                         InvalidCurieValue,
                         InvalidDatetimeValue,
                         InvalidNameValue,
                         InvalidHashValue,
                         InvalidIntegerValue,
                         InvalidPeriodValue,
                         InvalidTimestampValue,
                         InvalidUrlValue)


def validate(data: Dict[str, Union[str, List[str]]], schema: Schema) -> bool:
    if data.get(schema.primary_key) is None:
        raise MissingPrimaryKey(schema.primary_key, data)

    for key, value in data.items():
        attr = schema.get(key)

        if attr is None:
            raise UnknownAttribute(key, value)

        if value is None:
            return True

        if isinstance(value, List):
            if attr.cardinality is not Cardinality.Many:
                raise CardinalityMismatch(key, attr.cardinality.value, value)

            for el in value:
                validate_value(el, attr)

        else:
            if attr.cardinality is not Cardinality.One:
                raise CardinalityMismatch(key, attr.cardinality.value, value)

            validate_value(value, attr)

    return True


def validate_value(value: str, attr: Attribute):
    if not isinstance(value, str):
        raise RepresentationError(attr.uid, value, attr.datatype.value)

    validate_value_datatype(value, attr.datatype)


CURIE_RE = re.compile(r'^\w[\w\d-]*:[\w\d_/.%-]*$')
DATETIME_RE = re.compile(r'^\d{4}(-\d{2}(-\d{2}(T\d{2}(:\d{2}(:\d{2})?)?Z)?)?)?$') # NOQA
NAME_RE = re.compile(r'^\w[\w\d-]*$')
HASH_RE = re.compile(r'^sha-256:[a-f\d]{64}$')
INTEGER_RE = re.compile(r'^(0|[1-9]\d*)$')
PERIOD_RE = re.compile(r'^P(\d+Y)?(\d+M)?(\d+D)?(T(\d+H)?(\d+M)?(\d+S)?)?$')
TIMESTAMP_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
URL_RE = re.compile(r'^https?://')


def validate_value_datatype(value, datatype: Datatype) -> bool:
    if datatype is Datatype.Curie and CURIE_RE.match(value) is None:
        raise InvalidCurieValue(value)

    if datatype is Datatype.Datetime and DATETIME_RE.match(value) is None:
        raise InvalidDatetimeValue(value)

    if datatype is Datatype.Name and NAME_RE.match(value) is None:
        raise InvalidNameValue(value)

    if datatype is Datatype.Hash and HASH_RE.match(value) is None:
        raise InvalidHashValue(value)

    if datatype is Datatype.Integer and INTEGER_RE.match(value) is None:
        raise InvalidIntegerValue(value)

    if (datatype is Datatype.Period and
            (PERIOD_RE.match(value) is None or value == "P" or
             value.endswith("T"))):
        raise InvalidPeriodValue(value)

    if datatype is Datatype.Timestamp and TIMESTAMP_RE.match(value) is None:
        raise InvalidTimestampValue(value)

    if datatype is Datatype.Url and URL_RE.match(value) is None:
        raise InvalidUrlValue(value)

    # Datatype.String and Datatype.Text are assumed to be valid.
    return True
