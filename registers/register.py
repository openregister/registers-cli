"""
The Register representation and utilities to work with it.
"""

from typing import List, Dict
from .rsf.parser import Command
from .log import Log, collect
from .schema import Schema, attribute
from .exceptions import MissingIdentifier
from .entry import Entry
from .record import Record


class Register:
    """
    Represents a register.
    """

    def __init__(self):
        self._log = Log()
        self._metalog = Log()
        self._commands = []
        self._uid = None
        self._update_date = None

    def load_commands(self, commands: List[Command]):
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

        if not self._log.is_empty():
            self._update_date = self._log.entries[-1].timestamp
        elif not self._metalog.is_empty():
            self._update_date = self._metalog.entries[-1].timestamp

    def stats(self) -> Dict[str, int]:
        """
        Collects statistics from both logs.
        """

        return {
            "data": self._log.stats(),
            "metadata": self._metalog.stats()
        }

    @property
    def uid(self) -> str:
        """
        The register unique identifier.
        """

        return self._uid

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

    def record(self, key: str) -> Record:
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
            raise MissingIdentifier("A schema can't be derived unless the \
register has an identifier acting as \
primary key.")

        attrs = [attribute(value) for key, value
                 in self._metalog.snapshot().items()
                 if key.startswith("field:")]

        return Schema(self._uid, attrs)

    def context(self) -> Dict:
        """
        Collect the register context.
        """

        result = {
            # TODO
            "domain": "register.gov.uk",
            "total-records": len(self.records()),
            "total-entries": self._log.size,
            "register-record": self._metalog.find("fields"),
            "custodian": self._metalog.find("custodian"),
            "last-updated": self._update_date
        }

        return result

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
