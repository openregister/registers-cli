# -*- coding: utf-8 -*-

"""
This module implements the records command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from io import StringIO
import click
from .. import rsf, Register
from ..exceptions import RegistersException
from . import utils


@click.command(name="records")
@click.option("--format", "output_format", type=click.Choice(["json", "csv"]))
@click.argument("rsf_file", type=click.Path(exists=False))
def records_command(rsf_file, output_format):
    """
    Computes the records for the given RSF file.
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        records = register.records()

        if output_format == "json":
            stream = StringIO()
            utils.serialise_json(records, stream)

            stream.seek(0)

            click.echo(stream.read())

        elif output_format == "csv":
            # TODO:
            utils.error("Not implemented")

        else:
            for record in records.values():
                click.echo(record.blob)

    except RegistersException as err:
        utils.error(str(err))