import pytest
from registers.validator import validate, validate_value_datatype
from registers.schema import Schema, Cardinality, Datatype, Attribute
from registers.exceptions import (MissingPrimaryKey, CardinalityMismatch,
                                  RepresentationError, UnknownAttribute,
                                  InvalidCurieValue,
                                  InvalidDatetimeValue,
                                  InvalidNameValue,
                                  InvalidHashValue,
                                  InvalidIntegerValue,
                                  InvalidPeriodValue,
                                  InvalidTimestampValue,
                                  InvalidUrlValue)


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


def test_curie_value():
    assert validate_value_datatype("foo:bar", Datatype.Curie)
    assert validate_value_datatype("foo:", Datatype.Curie)
    assert validate_value_datatype("foo:bar_qux", Datatype.Curie)
    assert validate_value_datatype("foo:bar-qux", Datatype.Curie)
    assert validate_value_datatype("foo:bar/qux", Datatype.Curie)
    assert validate_value_datatype(r"foo:bar%F3", Datatype.Curie)


def test_invalid_curie_value():
    with pytest.raises(InvalidCurieValue):
        validate_value_datatype("abc", Datatype.Curie)

    with pytest.raises(InvalidCurieValue):
        validate_value_datatype("foo:bar:qux", Datatype.Curie)


def test_integer_value():
    assert validate_value_datatype("0", Datatype.Integer)
    assert validate_value_datatype("1", Datatype.Integer)
    assert validate_value_datatype("123", Datatype.Integer)


def test_invalid_integer_value():
    with pytest.raises(InvalidIntegerValue):
        validate_value_datatype("abc", Datatype.Integer)


def test_string_value():
    assert validate_value_datatype("foo", Datatype.String)


def test_datetime_value():
    assert validate_value_datatype("2019", Datatype.Datetime)
    assert validate_value_datatype("2019-02", Datatype.Datetime)
    assert validate_value_datatype("2019-02-20", Datatype.Datetime)
    assert validate_value_datatype("2019-02-20T10Z", Datatype.Datetime)
    assert validate_value_datatype("2019-02-20T10:11Z", Datatype.Datetime)
    assert validate_value_datatype("2019-02-20T10:11:12Z", Datatype.Datetime)


def test_invalid_datetime_value():
    with pytest.raises(InvalidDatetimeValue):
        validate_value_datatype("abc", Datatype.Datetime)

    with pytest.raises(InvalidDatetimeValue):
        validate_value_datatype("2019-03-17T10:11:12", Datatype.Datetime)


def test_timestamp_value():
    assert validate_value_datatype("2019-02-20T10:11:12Z", Datatype.Datetime)


def test_invalid_timestamp_value():
    with pytest.raises(InvalidTimestampValue):
        validate_value_datatype("abc", Datatype.Timestamp)

    with pytest.raises(InvalidTimestampValue):
        validate_value_datatype("2019-03-17T10:11:12", Datatype.Timestamp)


def test_period_value():
    assert validate_value_datatype("P1Y", Datatype.Period)
    assert validate_value_datatype("P10Y", Datatype.Period)
    assert validate_value_datatype("P1Y2M", Datatype.Period)
    assert validate_value_datatype("P1Y2M3D", Datatype.Period)
    assert validate_value_datatype("P1Y2M3DT4H", Datatype.Period)
    assert validate_value_datatype("P1Y2M3DT4H5M", Datatype.Period)
    assert validate_value_datatype("P1Y2M3DT4H5M6S", Datatype.Period)
    assert validate_value_datatype("P1Y2M3DT4H6S", Datatype.Period)
    assert validate_value_datatype("P1Y2M3DT6S", Datatype.Period)
    assert validate_value_datatype("P1Y2MT6S", Datatype.Period)
    assert validate_value_datatype("P1YT6S", Datatype.Period)
    assert validate_value_datatype("PT6S", Datatype.Period)
    assert validate_value_datatype("P1Y2M3DT4M6S", Datatype.Period)


def test_invalid_period_value():
    with pytest.raises(InvalidPeriodValue):
        validate_value_datatype("abc", Datatype.Period)

    with pytest.raises(InvalidPeriodValue):
        validate_value_datatype("PT", Datatype.Period)

    with pytest.raises(InvalidPeriodValue):
        validate_value_datatype("P", Datatype.Period)

    with pytest.raises(InvalidPeriodValue):
        validate_value_datatype("P2YT", Datatype.Period)


def test_url_value():
    assert validate_value_datatype("https://example.org", Datatype.Url)


def test_invalid_url_value():
    with pytest.raises(InvalidUrlValue):
        validate_value_datatype("abc", Datatype.Url)


def test_hash_value():
    assert validate_value_datatype("sha-256:b3ca21b3b3a795ab9cd1d10f3d447947328406984f8a461b43d9b74b58cccfe8", Datatype.Hash) # NOQA


def test_invalid_hash_value():
    with pytest.raises(InvalidHashValue):
        validate_value_datatype("abc", Datatype.Hash)

    with pytest.raises(InvalidHashValue):
        validate_value_datatype("sha-256:", Datatype.Hash)


def test_name_value():
    assert validate_value_datatype("start-date", Datatype.Name)


def test_invalid_name_value():
    with pytest.raises(InvalidNameValue):
        validate_value_datatype("foo/123", Datatype.Name)
