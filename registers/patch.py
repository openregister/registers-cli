"""
The Patch representation and utilities to work with it.
"""
from typing import List, cast, Union
from datetime import datetime
from .entry import Entry, Scope
from .blob import Blob
from .schema import Schema
from .rsf import Command, Action
from .core import format_timestamp


class Patch:
    """
    Represents a patch of data changes.
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
        return self._commands

    @property
    def schema(self):
        return self._schema

    @property
    def timestamp(self):
        return self._timestamp

    def add(self, blob: Blob):
        self._commands.extend(collect(self._schema.primary_key,
                                      [blob],
                                      self._timestamp))


def collect(pk: str, blobs: List[Blob], timestamp: str) -> List[Command]:
    """
    Collects commands from a list of blobs.
    """
    commands = []

    for blob in blobs:
        key = cast(str, blob.get(pk))
        entry = Entry(key, Scope.User, timestamp, blob.digest())
        commands.append(Command(Action.AddItem, blob))
        commands.append(Command(Action.AppendEntry, entry))

    return commands
