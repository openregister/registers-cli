# -*- coding: utf-8 -*-

"""
This module implements core functions.

:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

EMPTY_ROOT_HASH = "sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # NOQA
SHA256_PREFIX = "sha-256"

__version__ = "0.1.0"


def format_timestamp(datetime):
    """
    Formats a UTC datetime as a RFC3339 timestamp.

    Warning: UTC timezone is assumed.
    """

    return f"{datetime.isoformat(timespec='seconds')}Z"
