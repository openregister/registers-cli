# -*- coding: utf-8 -*-

"""
This module implements the Patch representation and utility functions to
operate on it.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from typing import List, cast, Union
from datetime import datetime
from .entry import Entry, Scope
from .blob import Blob
from .hash import Hash
from .schema import Schema
from .rsf import Command, Action, assert_root_hash, add_item, append_entry
from .core import format_timestamp


class Patch:
    """
    Represents a patch of data changes that can be applied to a Register.

    You can make a patch from a list of blobs:

    >>> from registers import rsf, schema, Schema, Blob, Entry, Hash
    >>> sch = Schema("foo", [schema.string("foo"), schema.string("bar")])
    >>> blobs = [Blob({"foo": "abc", "bar": "xyz"})]
    >>> timestamp = "2019-01-01T10:11:12Z"
    >>> patch = Patch(sch, blobs, timestamp)
    >>> patch.timestamp
    '2019-01-01T10:11:12Z'

    Or from a list of RSF commands:

    >>> cmds = [
    ...   rsf.add_item(Blob({"foo": "abc", "bar": "xyz"})),
    ...   rsf.append_entry(Entry("foo", Scope.User,
    ... timestamp, Hash("sha-256",
    ... "5dd4fe3b0de91882dae86b223ca531b5c8f2335d9ee3fd0ab18dfdc2871d0c61")))]
    >>> patch = Patch(sch, blobs, timestamp)
    >>> patch.timestamp
    '2019-01-01T10:11:12Z'
    """

    def __init__(self,
                 schema: Schema,
                 data: Union[List[Blob], List[Command]],
                 timestamp: str = None):

        self._schema = schema

        if not data:
            raise ValueError("A patch must receive some data")

        if isinstance(data[0], Blob):
            self._timestamp = timestamp or format_timestamp(datetime.utcnow())
            blobs = cast(List[Blob], data)
            self._commands = collect(schema.primary_key, blobs,
                                     self._timestamp)

        elif isinstance(data[0], Command):
            self._commands = cast(List[Command], data)
            self._timestamp = [cast(Entry, cmd.value).timestamp for cmd
                               in self._commands
                               if cmd.action == Action.AppendEntry][0]

    @property
    def commands(self):
        """
        The list of commands that constitute the patch.
        """

        return self._commands

    @property
    def schema(self):
        """
        The schema the patch data is checked against.
        """

        return self._schema

    @property
    def timestamp(self):
        """
        The timestamp used to generate all commands belonging to the patch.
        """

        return self._timestamp

    def add(self, blob: Blob):
        """
        Adds the given data to the patch.
        """

        self._commands.extend(collect(self._schema.primary_key,
                                      [blob],
                                      self._timestamp))

    def seal(self, start: Hash, end: Hash):
        """
        Seals the patch with the given hashes. It makes the patch applicable to
        a particular size of the register.
        """

        self._commands.insert(0, assert_root_hash(start))
        self._commands.append(assert_root_hash(end))

    def is_sealed(self) -> bool:
        """
        Checks if a patch is sealed.
        """

        return (self._commands[0].action == Action.AssertRootHash and
                self._commands[-1].action == Action.AssertRootHash)


def collect(primary_key: str, blobs: List[Blob],
            timestamp: str) -> List[Command]:
    """
    Collects commands from a list of blobs.
    """

    commands = []

    for blob in blobs:
        key = cast(str, blob.get(primary_key))
        entry = Entry(key, Scope.User, timestamp, blob.digest())
        commands.append(add_item(blob))
        commands.append(append_entry(entry))

    return commands
