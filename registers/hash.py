# -*- coding: utf-8 -*-

"""
This module implements the Hash representation.

:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""


class Hash:
    """
    Represents a hash value.

    Even though the specification accounts for the possibility of different
    algorithms, this implementation assumes SHA2-256 identified as
    ``sha-256``.

    >>> Hash("sha-256",
    ... "5dd4fe3b0de91882dae86b223ca531b5c8f2335d9ee3fd0ab18dfdc2871d0c61")
    sha-256:5dd4fe3b0de91882dae86b223ca531b5c8f2335d9ee3fd0ab18dfdc2871d0c61
    """

    def __init__(self, algorithm, digest):
        self._algorithm = algorithm
        self._digest = digest

    def __hash__(self) -> int:
        return int(self._digest, 16)

    def __eq__(self, other) -> bool:
        return (self.digest == other.digest and
                self.algorithm == other.algorithm)

    def __repr__(self):
        return f"{self._algorithm}:{self._digest}"

    @property
    def algorithm(self):
        """The algorithm that produced the hash digest"""

        return self._algorithm

    @property
    def digest(self):
        """The hex digest"""

        return self._digest
