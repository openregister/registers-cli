# -*- coding: utf-8 -*-

"""
Registers Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import click
from . import commands
from .core import __version__


@click.group()
@click.version_option(prog_name=click.style("registers", fg='bright_yellow'),
                      version=__version__)
def cli():
    """
    registers lets you manage a Register represented as a Register
    Serialisation Format (RSF).
    """


cli.add_command(commands.init_command)
cli.add_command(commands.build_command)
cli.add_command(commands.context_command)
cli.add_command(commands.records_command)
cli.add_command(commands.blob_group)
cli.add_command(commands.patch_group)
cli.add_command(commands.value_group)
