from typing import Dict, Union, List
from .blob import Blob
from .schema import Schema, Cardinality, Datatype
from .exceptions import (MissingPrimaryKey, CardinalityMismatch,
                         RepresentationError, UnknownAttribute)


def coerce(data: Dict[str, Union[str]], schema: Schema) -> Blob:
    """
    Takes a dictionary and attempts to coerce it as a Blob and validate
    against the given Schema.
    """

    # trim spaces
    # discard empty values as nully.
    # x  validate PK exists -- schema
    # validate values -- schema
    # x  validate fields exist in the schema -- schema
    # x  validate card -- schema
    # guard against equal blobs with different PK -- (out of scope) schema.

    # tsv only
    # validate card formatting (e.g. ;, do we allow spaces after ;?) -- schema

    # entry validation
    # validate key
    # validate timestamp
    # validate blob exists
    # validate previous entry for key has a different blob -- (out of scope)
    pass


def validate(data: Dict[str, Union[str]], schema: Schema) -> bool:
    if data.get(schema.primary_key) is None:
        raise MissingPrimaryKey(data)

    for key, value in data.items():
        attr = schema.get(key)

        if attr is None:
            raise UnknownAttribute((key, data))

        if value is None:
            return True

        validate_representation(key, value)

        if not check_cardinality(value, attr.cardinality):
            raise CardinalityMismatch((key, attr.cardinality, data))

    return True


def validate_representation(key: str, value):
    """
    Validates the value is a string or a list of strings.
    """

    if not check_representation(value):
        raise RepresentationError((key, value))

    if isinstance(value, List):
        for v in value:
            if not isinstance(v, str):
                raise RepresentationError((key, value))


def check_cardinality(value: Union[str, List[str]], cardinality: Cardinality):
    return ((cardinality is Cardinality.Many and isinstance(value, List)) or
            (cardinality is Cardinality.One and isinstance(value, str)))


def check_representation(value):
    return isinstance(value, str) or isinstance(value, List)
