from registers.rsf.core import Command, Action
from registers.blob import Blob
from registers.entry import Entry, Scope
from registers.hash import Hash


def test_serialize_add_item_command():
    expected = 'add-item	{"register-name":"Country"}'
    value = Blob({"register-name": "Country"})
    command = Command(Action.AddItem, value)

    assert str(command) == expected


def test_serialize_append_entry_command():
    expected = 'append-entry	system	name	2017-07-17T10:59:47Z	sha-256:d3d8e15fbd410e08bd896902fba40d4dd75a4a4ae34d98b87785f4b6965823ba' # NOQA
    value = Entry(
        "name",
        Scope.System,
        "2017-07-17T10:59:47Z",
        Hash("sha-256", "d3d8e15fbd410e08bd896902fba40d4dd75a4a4ae34d98b87785f4b6965823ba") # NOQA
    )
    command = Command(Action.AppendEntry, value)

    assert str(command) == expected


def test_serialize_assert_root_hash_command():
    expected = "assert-root-hash	sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # NOQA
    value = Hash(
        "sha-256",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
    command = Command(Action.AssertRootHash, value)

    assert str(command) == expected
