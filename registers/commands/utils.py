# -*- coding: utf-8 -*-

"""
This module implements helper functions for the CLI commands.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import json
import click
from .. import Register, Blob, Entry, Record, Hash, Schema, Attribute
from ..exceptions import CommandError


def error(message):
    """
    Sends a message to stderr and exits with code error 1.
    """

    click.secho(message, fg="red", bold=True, err=True)
    exit(1)


def note(message):
    """
    Sends a message to stdout.
    """

    click.secho(message, fg="yellow", bold=True)


def success(message):
    """
    Sends a message to stdout.
    """

    click.secho(message, fg="green", bold=True)


def check_readiness(register: Register):
    """
    Helper to raise an exception if the register is not ready to be used.
    """

    if not register.is_ready():
        msg = "The given RSF does not have enough information to be used in \
this command."
        raise CommandError(msg)


def serialise_json(obj, stream):
    """
    Helper to serialise to JSON.
    """

    json.dump(obj, stream, ensure_ascii=False, indent=2, cls=JsonEncoder)


class JsonEncoder(json.JSONEncoder):
    """
    JSON encoder for registers types.
    """

    def default(self, obj):  # pylint: disable=E0202,W0221
        if isinstance(obj, Hash):
            return repr(obj)

        if isinstance(obj, (Blob, Entry, Record, Schema, Attribute)):
            return obj.to_dict()

        return json.JSONEncoder.default(self, obj)


def progressbar(iterable, **kwargs):
    """
    Progressbar customisation.

    Short limit is overriten to ensure the progressbar always shows up.
    """

    tpl = click.style("[%(bar)s] %(info)s %(label)s", fg="bright_yellow")
    bar = click.progressbar(iterable,
                            show_eta=False,
                            show_percent=True,
                            bar_template=tpl,
                            **kwargs)

    bar.short_limit = 0.1

    return bar
