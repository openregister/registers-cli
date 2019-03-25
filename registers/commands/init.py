# -*- coding: utf-8 -*-

"""
This module implements the init command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import os
import click
from ..core import EMPTY_ROOT_HASH


@click.command(name="init")
@click.argument("filepath", type=click.Path(exists=False))
def init_command(filepath):
    """Creates an empty register."""

    assert_root_hash = f"assert-root-hash\t{EMPTY_ROOT_HASH}"

    if os.path.exists(filepath):
        raise click.UsageError("Please select a file that does not exist.")

    with click.open_file(filepath, "w", "utf-8") as handle:
        handle.write(assert_root_hash)

    fname = click.style(click.format_filename(filepath), fg='bright_yellow')
    click.echo(f"Empty register successfully created at {fname}")
