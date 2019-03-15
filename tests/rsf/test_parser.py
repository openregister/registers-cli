import pytest
import io
from registers.rsf.core import Action
from registers.rsf.parser import load, parse, parse_command
from registers import Blob, Entry, Scope, Hash
from registers.rsf.exceptions import (AppendEntryCommandException,
                                      AddItemCommandException,
                                      AssertRootHashCommandException)


def test_parse():
    commands = io.StringIO("""assert-root-hash	sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
add-item	{"register-name":"Country"}
append-entry	system	name	2017-07-17T10:59:47Z	sha-256:d3d8e15fbd410e08bd896902fba40d4dd75a4a4ae34d98b87785f4b6965823ba
""") # NOQA
    actual = parse(commands)

    assert len(actual) == 3


def test_load():
    commands = """assert-root-hash	sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
add-item	{"register-name":"Country"}
append-entry	system	name	2017-07-17T10:59:47Z	sha-256:d3d8e15fbd410e08bd896902fba40d4dd75a4a4ae34d98b87785f4b6965823ba
""" # NOQA
    actual = load(commands)

    assert len(actual) == 3


def test_parse_add_item_command():
    expected = Blob({"register-name": "Country"})
    command = 'add-item	{"register-name":"Country"}'
    actual = parse_command(command)

    assert actual.action == Action.AddItem
    assert actual.value == expected


def test_unexpected_add_item_command():
    command = 'add-item	{register-name":"Country"}'

    with pytest.raises(AddItemCommandException):
        parse_command(command)


def test_parse_append_entry_command():
    expected = Entry(
        "name",
        Scope.System,
        "2017-07-17T10:59:47Z",
        Hash("sha-256", "d3d8e15fbd410e08bd896902fba40d4dd75a4a4ae34d98b87785f4b6965823ba") # NOQA
    )
    command = 'append-entry	system	name	2017-07-17T10:59:47Z	sha-256:d3d8e15fbd410e08bd896902fba40d4dd75a4a4ae34d98b87785f4b6965823ba' # NOQA
    actual = parse_command(command)

    assert actual.action == Action.AppendEntry
    assert actual.value == expected


def test_unexpected_append_entry_command():
    command = 'append-entry	system	name'

    with pytest.raises(AppendEntryCommandException):
        parse_command(command)


def test_parse_assert_root_command():
    expected = Hash(
        "sha-256",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
    command = "assert-root-hash	sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # NOQA
    actual = parse_command(command)

    assert actual.action == Action.AssertRootHash
    assert actual.value == expected


def test_unexpected_assert_root_command():
    command = 'assert-root-hash	name'

    with pytest.raises(AssertRootHashCommandException):
        parse_command(command)
