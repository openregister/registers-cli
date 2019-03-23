# -*- coding: utf-8 -*-

"""
This module implements the RSF exceptions.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""


class UnknownCommand(Exception):
    """An unknown command was found."""


class UnexpectedEntry(Exception):
    """An entry with an unexpected structure was found."""


class UnexpectedBlob(Exception):
    """A blob with an unexpected structure was found."""


class AppendEntryCommandException(Exception):
    """Unexpected append-entry command"""


class AddItemCommandException(Exception):
    """Unexpected add-item command"""


class AssertRootHashCommandException(Exception):
    """Unexpected assert-root-hash command."""
