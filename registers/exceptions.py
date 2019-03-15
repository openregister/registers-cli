"""
Exceptions for the registers package.
"""


class OrphanEntry(Exception):
    """Found an entry with a reference to a missing blob."""


class InsertException(Exception):
    """Attempted to insert an unknown type of object."""


class AttributeAlreadyExists(Exception):
    """Attempted to insert a duplicate attribute."""


class MissingIdentifier(Exception):
    """Found a register without identifier."""


class InconsistentRecord(Exception):
    """Found a record with a blob that does not belong to the entry."""
