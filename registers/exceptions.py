"""
RegistersExceptions for the registers package.
"""


class RegistersException(Exception):
    """Found an entry with a reference to a missing blob."""


class OrphanEntry(RegistersException):
    """Found an entry with a reference to a missing blob."""
    def __init__(self, entry):
        message = f"Entry {entry.position} for key {entry.key} points to an \
unknown blob ({entry.blob_hash})"

        super().__init__(message)


class InsertException(RegistersException):
    """Attempted to insert an unknown type of object."""


class AttributeAlreadyExists(RegistersException):
    """Attempted to insert a duplicate attribute."""


class MissingIdentifier(RegistersException):
    """Found a register without identifier."""


class InconsistentRecord(RegistersException):
    """Found a record with a blob that does not belong to the entry."""


class ValidationError(RegistersException):
    """A blob validation error."""


class MissingEntryKey(RegistersException):
    """Found an entry without key."""
    def __init__(self):
        message = f"Entries must have a key."

        super().__init__(message)


class MissingAttributeIdentifier(RegistersException):
    """Found an attribute without identifier."""
    def __init__(self):
        message = f"Attributes must have a unique identifier."

        super().__init__(message)


class UnknownAttribute(ValidationError):
    """Found an unknown attribute."""
    def __init__(self, attr, value):
        message = f"The attribute '{attr}' in '{value}' is not present in the \
schema."

        super().__init__(message)


class MissingPrimaryKey(ValidationError):
    """Found a blob without the primary key."""
    def __init__(self, pk, value):
        message = f"The primary key attribute '{pk}' must be present in \
'{value}'."

        super().__init__(message)


class CardinalityMismatch(ValidationError):
    """Found a value with the wrong cardinality."""
    def __init__(self, attr, card, value):
        message = f"The attribute '{attr}' expects {value} to be cardinality \
'{card}'."

        super().__init__(message)


class DuplicatedEntry(ValidationError):
    """Attempted to apply an entry that already exists in the Log."""
    def __init__(self, key, blob):
        message = (f"The latest entry for {key} already "
                   f"has blob {blob.to_json()}.")

        super().__init__(message)


class InconsistentLog(ValidationError):
    """
    The given log is not consistent with the given root hash.
    """

    def __init__(self, expected, actual, size):
        message = (f"The log at size {size} was expected to have a root hash"
                   f"\n  {expected}"
                   f"\nbut it is"
                   f"\n  {actual}")

        super().__init__(message)


class RepresentationError(ValidationError):
    """
    Found a value that does not conform the string representation for the
    expected datatype.
    """

    def __init__(self, attr, value, datatype):
        message = f"The value for '{attr}' has a value '{value}' that is not a \
string representation for '{datatype}'."

        super().__init__(message)


class InvalidValue(ValidationError):
    """
    Found an invalid value.
    """

    def __init__(self, datatype, value):
        self._datatype = value
        self._value = value

        message = f"'{value}' is not a valid '{datatype}'."

        super().__init__(message)

    @property
    def datatype(self):
        """The expected datatype"""

        return self._datatype

    @property
    def value(self):
        """The invalid value."""

        return self._value


class InvalidKey(ValidationError):
    """
    Found an invalid key.
    """

    def __init__(self, value):
        message = f"'{value}' is not a valid key."

        super().__init__(message)


class InvalidCurieValue(InvalidValue):
    """
    Found an invalid curie.
    """

    def __init__(self, value):
        super().__init__("curie", value)


class InvalidDatetimeValue(InvalidValue):
    """
    Found an invalid datetime.
    """

    def __init__(self, value):
        super().__init__("datetime", value)


class InvalidNameValue(InvalidValue):
    """
    Found an invalid name.
    """

    def __init__(self, value):
        super().__init__("name", value)


class InvalidHashValue(InvalidValue):
    """
    Found an invalid hash.
    """

    def __init__(self, value):
        super().__init__("hash", value)


class InvalidIntegerValue(InvalidValue):
    """
    Found an invalid integer.
    """

    def __init__(self, value):
        super().__init__("integer", value)


class InvalidPeriodValue(InvalidValue):
    """
    Found an invalid period.
    """

    def __init__(self, value):
        super().__init__("period", value)


class InvalidTimestampValue(InvalidValue):
    """
    Found an invalid timestamp.
    """

    def __init__(self, value):
        super().__init__("timestamp", value)


class InvalidUrlValue(InvalidValue):
    """
    Found an invalid url.
    """

    def __init__(self, value):
        super().__init__("url", value)


class CommandError(RegistersException):
    """
    Found a command error.
    """
