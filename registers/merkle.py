# -*- coding: utf-8 -*-

"""
This module implements the Merkle tree algorithm.

:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from hashlib import sha256
from typing import List, Callable


Leaf = bytes
Digest = bytes
Level = List[Digest]


class Tree:
    """
    Represents a Merkle tree.

    A tree such as:

                  ___ i = h(h+e) ___
                 |                   |
           _ h = h(f+g) _            |
          |              |           |
      f = h(a+b)     g = h(c+d)      |
      |        |     |        |      |
      a        b     c        d      e

    Is represented as a sequence of levels where orphan nodes are replicated in
    the next level:

        [
            [a, b, c, d, e], -- level 0
            [f, g, e],       -- level 1
            [h, e],          -- level 2
            [i],             -- root
        ]

    Leaves and nodes are tagged with 0x00 and 0x01 respectively as defined in
    RFC 6962, section 2.1 https://tools.ietf.org/html/rfc6962#section-2.1
    """

    def __init__(self, leaves: List[Leaf]):
        self._hash_fun = sha256
        self._leaves = leaves
        self._levels = build_levels(self._leaves, self._hash_fun)
        self._height = len(self._levels)

    @property
    def root_hash(self) -> Digest:
        """
        The root hash.
        """

        return self._levels[-1][0]

    @property
    def leaves(self) -> List[Leaf]:
        """
        The original leaves.
        """

        return self._leaves

    @property
    def levels(self) -> List[Level]:
        """
        The tree levels including the root level.
        """

        return self._levels

    @property
    def height(self) -> int:
        """
        The height of the tree. Or, number of levels.
        """

        return self._height


def build_levels(leaves: List[Leaf], fun: Callable) -> List[Level]:
    """
    Builds all levels from the given list of leaves.

    >>> level = [hash_empty(sha256)]
    >>> build_levels([], sha256)[0] == level
    True

    >>> len(build_levels([], sha256))
    1
    """

    levels = [[hash_leaf(leaf, fun) for leaf in leaves]]

    if not leaves:
        return [[hash_empty(fun)]]

    if len(leaves) == 1:
        return levels

    while True:
        idx = len(levels)

        levels.append(build_level(levels[idx - 1], fun))

        if len(levels[idx]) == 1:
            break

    return levels


def build_level(level: Level, fun: Callable) -> Level:
    """
    Builds a level of nodes from the given level.

    >>> build_level([], sha256)[0].hex()
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

    >>> from binascii import unhexlify
    >>> level = [unhexlify(('e3b0c44298fc1c149afbf4c8996fb924'
    ...                     '27ae41e4649b934ca495991b7852b855'))]
    >>> build_level(level, sha256)[0].hex()
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    """

    next_level = []

    if not level:
        return [hash_empty(fun)]

    if len(level) == 1:
        return level

    for left, right in zip(level[0::2], level[1::2]):
        next_level.append(hash_node(left, right, fun))

    if len(level) % 2 == 1:
        next_level.append(level[-1])

    return next_level


def hash_node(left: Digest, right: Digest, fun: Callable) -> Digest:
    """
    Hashes a new node from two nodes from the previous level.
    """

    hasher = fun(b"\x01")
    hasher.update(left + right)

    return hasher.digest()


def hash_leaf(leaf: Leaf, fun: Callable) -> Digest:
    """
    Hashes a leaf.
    """

    hasher = fun(b"\x00")
    hasher.update(leaf)

    return hasher.digest()


def hash_empty(fun: Callable) -> Digest:
    """
    Hashes the empty tree.

    >>> hash_empty(sha256).hex()
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    """

    return fun(b"").digest()
