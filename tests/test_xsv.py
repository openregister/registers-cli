import pytest
from registers import rsf, xsv, schema, Schema, Blob, Register
from registers.exceptions import InvalidKey
from io import StringIO


@pytest.fixture
def isa_register():
    filename = "tests/fixtures/information-sharing-agreement-0001.rsf"
    with open(filename, "r") as handle:
        commands = rsf.parse(handle.readlines())
        register = Register(commands)

        return register


@pytest.fixture
def isa_tsv_patch(isa_register):
    filename = "tests/fixtures/2019-02-07_update_isa-main.tsv"
    with open(filename, "r", newline="") as handle:
        return xsv.deserialise(handle, isa_register.schema())


def test_serialise_value():
    assert xsv.serialise_value("foo") == "foo"
    assert xsv.serialise_value(["foo"]) == "foo"
    assert xsv.serialise_value(["foo", "bar"]) == "foo;bar"


def test_deserialise_tsv():
    tsv = """foo	x	y
first	1	1
second	2	1
third	3	2
"""
    sch = Schema("foo", [
        schema.string("foo"),
        schema.integer("x"),
        schema.integer("y")
    ])
    expected = [
        Blob({"foo": "first", "x": "1", "y": "1"}),
        Blob({"foo": "second", "x": "2", "y": "1"}),
        Blob({"foo": "third", "x": "3", "y": "2"}),
    ]

    actual = xsv.deserialise(StringIO(tsv), sch)

    assert actual == expected


def test_deserialise_isa_tsv_patch(isa_tsv_patch):
    size = len(isa_tsv_patch)
    assert size == 3


def test_deserialise_isa_tsv_patch_item(isa_tsv_patch):
    item = isa_tsv_patch[0]

    assert isinstance(item, Blob)


def test_coerce_wrong_key():
    sch = Schema("foo", [
        schema.string("foo"),
        schema.integer("x"),
        schema.integer("y")
    ])
    data = {"foo": "_1", "x": "1", "y": "1"}

    with pytest.raises(InvalidKey):
        xsv.coerce(data, sch)
