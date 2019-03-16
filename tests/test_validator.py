import pytest
from registers.validator import validate
from registers.schema import Schema, Cardinality, Datatype, Attribute
from registers.exceptions import (MissingPrimaryKey, CardinalityMismatch,
                                  RepresentationError, UnknownAttribute)


def test_valid_string():
    data = {
        "id": "foo",
        "abc": "xyz"
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.String, Cardinality.One)]
    )

    assert validate(data, schema)


def test_valid_n_string():
    data = {
        "id": "foo",
        "abc": ["xyz"]
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.String, Cardinality.Many)]
    )

    assert validate(data, schema)


def test_missing_pk():
    data = {
        "abc": "xyz"
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.String, Cardinality.One)]
    )

    with pytest.raises(MissingPrimaryKey):
        validate(data, schema)


def test_unexpected_attribute():
    data = {
        "id": "foo",
        "abc": "xyz"
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One)]
    )

    with pytest.raises(UnknownAttribute):
        validate(data, schema)


def test_cardinality_n_mismatch():
    data = {
        "id": "foo",
        "abc": "xyz"
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.String, Cardinality.Many)]
    )

    with pytest.raises(CardinalityMismatch):
        validate(data, schema)


def test_cardinality_1_mismatch():
    data = {
        "id": "foo",
        "abc": ["xyz"]
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.String, Cardinality.One)]
    )

    with pytest.raises(CardinalityMismatch):
        validate(data, schema)


def test_representation_error_number():
    data = {
        "id": "foo",
        "abc": 1
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.Integer, Cardinality.One)]
    )

    with pytest.raises(RepresentationError):
        validate(data, schema)


def test_representation_error_bool():
    data = {
        "id": "foo",
        "abc": True
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.Integer, Cardinality.One)]
    )

    with pytest.raises(RepresentationError):
        validate(data, schema)


def test_representation_error_dict():
    data = {
        "id": "foo",
        "abc": {}
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.Integer, Cardinality.One)]
    )

    with pytest.raises(RepresentationError):
        validate(data, schema)


def test_representation_error_n_number():
    data = {
        "id": "foo",
        "abc": [1]
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.Integer, Cardinality.Many)]
    )

    with pytest.raises(RepresentationError):
        validate(data, schema)


def test_nully():
    data = {
        "id": "foo",
        "abc": None
    }

    schema = Schema(
        "id",
        [Attribute("id", Datatype.String, Cardinality.One),
         Attribute("abc", Datatype.Integer, Cardinality.One)]
    )

    assert validate(data, schema)
