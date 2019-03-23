# -*- coding: utf-8 -*-

"""
This module implements the RSF parser.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""


from typing import List, TextIO, Union
import json
from ..blob import Blob
from ..entry import Entry, Scope
from ..hash import Hash
from .exceptions import (UnknownCommand,
                         AppendEntryCommandException,
                         AddItemCommandException,
                         AssertRootHashCommandException)
from .core import Action, Command


def load(original: str) -> List[Command]:
    """
    Expects an RSF stringified patch (i.e. list of commands).
    """

    return parse(original.splitlines())


def parse(patch_lines: Union[List[str], TextIO]) -> List[Command]:
    """
    Parses a list of RSF stringified commands.
    """

    return [parse_command(token) for token in patch_lines]


def parse_command(original: str) -> Command:
    """
    Parses an RSF stringified command.

    Throws `UnknownCommand` when the action is unknown.
    """
    try:
        action, rest = original.split("\t", 1)
    except ValueError:
        raise UnknownCommand(original)

    if action == Action.AddItem.value:
        try:
            return Command(Action.AddItem, parse_blob(rest))
        except ValueError:
            raise AddItemCommandException(original)

    elif action == Action.AppendEntry.value:
        try:
            return Command(Action.AppendEntry, parse_entry(rest))
        except ValueError:
            raise AppendEntryCommandException(original)

    elif action == Action.AssertRootHash.value:
        try:
            return Command(Action.AssertRootHash, parse_hash(rest))
        except ValueError:
            raise AssertRootHashCommandException(original)

    else:
        raise UnknownCommand(original)


def parse_blob(original: str) -> Blob:
    """
    Parses a JSON string into a ``Blob``.
    """

    return Blob(json.loads(original.strip()))


def parse_entry(original: str) -> Entry:
    """
    Parses a string into an ``Entry``.
    """

    scope, key, timestamp, blob_hash = original.strip().split("\t")

    return Entry(
        key,
        Scope(scope),
        timestamp,
        parse_hash(blob_hash)
    )


def parse_hash(original: str) -> Hash:
    """
    Parses a V1 hash value.
    """

    algorithm, digest = original.strip().split(':')

    return Hash(algorithm, digest)
