import pytest
from registers import (rsf, xsv, schema, Register, Schema, Blob, Entry, Scope,
                       Patch, Hash)


@pytest.fixture
def fec_register():
    filename = "tests/fixtures/further-education-college-uk.rsf"
    commands = rsf.read(filename)
    register = Register(commands)

    return register


@pytest.fixture
def fec_old_patch():
    """
    Further Education College UK RSF patch generated with the old
    `rsfcreate.py` script.
    """
    with open("tests/fixtures/fec_old_patch.rsf") as handle:
        return handle.read().splitlines()


def test_patch():
    sch = Schema("foo", [
        schema.string("foo"),
        schema.integer("x"),
        schema.integer("y")
    ])
    blobs = [
        Blob({"foo": "first", "x": "1", "y": "1"}),
        Blob({"foo": "second", "x": "2", "y": "1"}),
        Blob({"foo": "third", "x": "3", "y": "2"}),
    ]
    timestamp = "2019-01-01T10:11:12Z"
    patch = Patch(sch, blobs, timestamp)
    expected = [
        rsf.Command(rsf.Action.AddItem,
                    Blob({"foo": "first", "x": "1", "y": "1"})),
        rsf.Command(
            rsf.Action.AppendEntry,
            Entry("first", Scope.User, timestamp,
                  Hash("sha-256",
                       "d8c619d437b4bc234ee39967b1578f4124e0cb672a214ef437bb3b5a3dde5d6a"))), # NOQA

        rsf.Command(rsf.Action.AddItem,
                    Blob({"foo": "second", "x": "2", "y": "1"})),
        rsf.Command(
            rsf.Action.AppendEntry,
            Entry("second", Scope.User, timestamp,
                  Hash("sha-256",
                       "5f99ce37f11cccc259fdf119137953363fb82f90af4520c6d66dc8ca4207d7ea"))), # NOQA

        rsf.Command(rsf.Action.AddItem,
                    Blob({"foo": "third", "x": "3", "y": "2"})),
        rsf.Command(
            rsf.Action.AppendEntry,
            Entry("third", Scope.User, timestamp,
                  Hash("sha-256",
                       "020d6a2e8888ad3d41b642ac511c4cc6411a299f3720c7dad8796d18853300aa"))) # NOQA
    ]

    assert patch.commands == expected


def test_regression_fec_patch(fec_register, fec_old_patch):
    sch = fec_register.schema()
    timestamp = "2019-03-21T20:02:59Z"
    fec_patch_filename = "tests/fixtures/fec_patch.tsv"

    with open(fec_patch_filename, "r", newline="") as handle:
        blobs = xsv.deserialise(handle, sch)
        patch = Patch(sch, blobs, timestamp)

        fec_register.apply(patch)

        print(list(zip(fec_old_patch, patch.commands)))

        for old, new in zip(fec_old_patch, patch.commands):
            assert old == repr(new)
