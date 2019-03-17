"""
RegistersExceptions for the registers package.
"""


class RegistersException(Exception):
    """Found an entry with a reference to a missing blob."""


class OrphanEntry(RegistersException):
    """Found an entry with a reference to a missing blob."""


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


class RepresentationError(ValidationError):
    def __init__(self, attr, value, datatype):
        message = f"The value for '{attr}' has a value '{value}' that is not a \
string representation for '{datatype}'."

        super().__init__(message)


class InvalidValue(ValidationError):
    def __init__(self, datatype, value):
        self._datatype = value
        self._value = value

        message = f"The value {value} is not a valid {datatype}."

        super().__init__(message)

        @property
        def datatype(self):
            self._datatype

        @property
        def value(self):
            self._value


class InvalidCurieValue(InvalidValue):
    def __init__(self, value):
        super().__init__("curie", value)


class InvalidDatetimeValue(InvalidValue):
    def __init__(self, value):
        super().__init__("datetime", value)


class InvalidNameValue(InvalidValue):
    def __init__(self, value):
        super().__init__("name", value)


class InvalidHashValue(InvalidValue):
    def __init__(self, value):
        super().__init__("hash", value)


class InvalidIntegerValue(InvalidValue):
    def __init__(self, value):
        super().__init__("integer", value)


class InvalidPeriodValue(InvalidValue):
    def __init__(self, value):
        super().__init__("period", value)


class InvalidTimestampValue(InvalidValue):
    def __init__(self, value):
        super().__init__("timestamp", value)


class InvalidUrlValue(InvalidValue):
    def __init__(self, value):
        super().__init__("url", value)
