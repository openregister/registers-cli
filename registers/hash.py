class Hash:
    """
    Represents a hash value.
    """

    def __init__(self, algorithm, digest):
        self._algorithm = algorithm
        self._digest = digest

    def __hash__(self):
        return self._digest

    def __eq__(self, other):
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
