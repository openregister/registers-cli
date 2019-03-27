# -*- coding: utf-8 -*-

"""
This module implements the Register representation and helper functions.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from typing import List, Dict, Optional, cast
from .rsf.parser import Command
from .log import Log, collect
from .schema import Schema, attribute
from .exceptions import MissingIdentifier
from .entry import Entry
from .record import Record
from .patch import Patch


class Register:
    """
    Represents a register.
    """

    def __init__(self, commands: List[Command] = None):
        self._log = Log()
        self._metalog = Log()
        self._commands: List[Command] = []
        self._uid = None
        self._update_date = None

        if commands is not None:
            self._load_commands(commands)

    def _load_commands(self, commands: List[Command]):
        """
        Attempts to process the given commands and build the log and metalog.
        """

        if commands:
            pair = collect(commands)

            self._commands = commands
            self._log = pair["data"]
            self._metalog = pair["metadata"]
            self._collect_basic_metadata()

    def _collect_basic_metadata(self):
        name_blob = self._metalog.find("name")
        if name_blob:
            self._uid = name_blob.get("name")
        self._collect_update_date()

    def _collect_update_date(self):
        if not self._log.is_empty():
            self._update_date = self._log.entries[-1].timestamp
        elif not self._metalog.is_empty():
            self._update_date = self._metalog.entries[-1].timestamp

    def apply(self, patch: Patch):
        """
        Attempts to apply the given patch to the Register.
        """
        pair = collect(patch.commands, self._log, self._metalog)
        self._log = pair["data"]
        self._metalog = pair["metadata"]
        self._commands.extend(patch.commands)
        self._collect_update_date()

    def stats(self) -> Dict[str, int]:
        """
        Collects statistics from both logs.
        """

        return {
            "data": self._log.stats(),
            "metadata": self._metalog.stats()
        }

    @property
    def uid(self) -> Optional[str]:
        """
        The register unique identifier.
        """

        return self._uid

    @property
    def commands(self):
        """
        The list of RSF commands.
        """
        return self._commands

    @property
    def log(self) -> Log:
        """
        The log of user entries.
        """

        return self._log

    @property
    def metalog(self) -> Log:
        """
        The log of system entries.
        """
        return self._metalog

    def records(self) -> Dict[str, Record]:
        """
        Computes the latest log state.
        """

        return self._log.snapshot()

    def record(self, key: str) -> Optional[Record]:
        """
        Collects the record for the given key.
        """

        return self._log.find(key)

    def trail(self, key: str) -> List[Entry]:
        """
        Collects the trail of change for the given key.
        """

        return self._log.trail(key)

    def schema(self) -> Schema:
        """
        Computes the current schema out of the metalog.
        """

        if self._uid is None:
            raise MissingIdentifier("The schema can't be derived unless the \
register has an identifier.")

        attrs = [attribute(value) for key, value
                 in self._metalog.snapshot().items()
                 if key.startswith("field:")]

        return Schema(self._uid, attrs)

    def context(self) -> Dict:
        """
        Collect the register context.
        """

        if self._uid is None:
            raise MissingIdentifier(("The context can't be derived unless the "
                                     "register has an identifier."))

        result = {
            "total-records": len(self.records()),
            "total-entries": self._log.size,
            "last-updated": self._update_date
        }

        fname = f"register:{self._uid}"

        if self._metalog.find(fname) is not None:
            result["register-record"] = (self._metalog.find(fname)
                                         .blob.to_dict())

        if self._metalog.find("custodian") is not None:
            result["custodian"] = (self._metalog.find("custodian")
                                   .blob.get("custodian"))

        return result

    def title(self) -> Optional[str]:
        """
        The human readable title.
        """
        record = cast(Record, self._metalog.find("register-name"))

        return cast(Optional[str], record.blob.get("register-name"))

    def description(self) -> Optional[str]:
        """
        The human readable description.
        """
        key = f"register:{self.uid}"
        record = cast(Record, self._metalog.find(key))

        return cast(Optional[str], record.blob.to_dict().get("text"))

    def is_ready(self) -> bool:
        """
        Checks if the register is ready for data to be inserted.

        A register is considered ready if:

        * It has an identifier acting as primary key.
        * It has a primary attribute.
        * It has a schema with at least one non primary attribute.
        """
        return self._uid is not None and self.schema().is_ready()

    def is_empty(self) -> bool:
        """
        Checks if the register has any data.

        A register is considered empty if the log is empty.
        """
        return self._log.is_empty()
