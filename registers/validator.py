# -*- coding: utf-8 -*-

"""
This module implements the validation functions for values.

:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import re
from urllib.parse import urlparse
from typing import Dict, Union, List, cast
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
    """
    Validates a blob-like dictionary against the given schema.

    If the given data is invalid it raises a ``ValidationError`` exception.
    """

    if data.get(schema.primary_key) is None:
        raise MissingPrimaryKey(schema.primary_key, data)

    for key, value in data.items():
        attr = schema.get(key)

        if attr is None:
            raise UnknownAttribute(key, value)

        if value is None:
            continue

        if isinstance(value, List):
            if attr.cardinality is not Cardinality.Many:
                raise CardinalityMismatch(key, attr.cardinality.value, value)

            for token in value:
                validate_value(token, attr)

        else:
            if attr.cardinality is not Cardinality.One:
                raise CardinalityMismatch(key, attr.cardinality.value, value)

            validate_value(value, attr)

    return True


def validate_value(value: str, attr: Attribute):
    """
    Validates a value against the given attribute.

    If the given value is invalid it raises a ``ValidationError`` exception.
    """

    if not isinstance(value, str):
        raise RepresentationError(attr.uid, value, attr.datatype.value)

    validate_value_datatype(value, attr.datatype)


CURIE_RE = re.compile(r'^[a-z][a-z\d-]*:[\w\d_/.%-]*$')
DATETIME_RE = re.compile(r'^\d{4}(-\d{2}(-\d{2}(T\d{2}(:\d{2}(:\d{2})?)?Z)?)?)?$') # NOQA
NAME_RE = re.compile(r'^[A-Za-z][A-Za-z\d-]*$')
KEY_RE = re.compile(r'^[A-Za-z\d][A-Za-z\d_./-]*$')
KEY_CONSECUTIVE_RE = re.compile(r'.*[_./-]{2}.*')
HASH_RE = re.compile(r'^sha-256:[a-f\d]{64}$')
INTEGER_RE = re.compile(r'^(0|\-?[1-9]\d*)$')
PERIOD_RE = re.compile(r'^P(\d+Y)?(\d+M)?(\d+D)?(T(\d+H)?(\d+M)?(\d+S)?)?$')
TIMESTAMP_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')


def validate_value_datatype(value: str, datatype: Datatype) -> bool:
    """
    Validates a value against the given datatype.

    If the given value is invalid it raises a ``InvalidValue`` exception.
    """

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

    if datatype is Datatype.Period:
        if value.find("/") != -1:
            start, end = value.split("/")

            if not (_is_valid_period_part(start)
                    and _is_valid_period_part(end)):
                raise InvalidPeriodValue(value)

        elif not _is_valid_duration(value):
            raise InvalidPeriodValue(value)

    if datatype is Datatype.Timestamp and TIMESTAMP_RE.match(value) is None:
        raise InvalidTimestampValue(value)

    if datatype is Datatype.Url:
        try:
            result = urlparse(value)
            is_known_scheme = result.scheme in ["http", "https"]
            has_hostname = result.hostname and result.hostname.find(".") != -1

            if not (is_known_scheme and has_hostname):
                raise InvalidUrlValue(value)

        except ValueError:
            raise InvalidUrlValue(value)

    # Datatype.String and Datatype.Text are assumed to be valid.
    return True


def validate_key(key: str) -> bool:
    """
    Validates a key value.
    """

    return cast(bool, KEY_RE.match(key) and not KEY_CONSECUTIVE_RE.match(key))


def _is_valid_duration(value):
    return (PERIOD_RE.match(value) is not None
            and value != "P"
            and not value.endswith("T"))


def _is_valid_period_part(value):
    return DATETIME_RE.match(value) or _is_valid_duration(value)
