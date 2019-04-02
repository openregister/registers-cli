# -*- coding: utf-8 -*-

"""
This module implements the record command group.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from io import StringIO
import click
from .. import rsf, xsv, Register, Record
from ..exceptions import RegistersException
from . import utils


@click.group(name="record")
def record_group():
    """
    Record operations.

    For example, you can list the available records in CSV:

        record list path/to/country.rsf

    Or get the record for the given key:

        record show --rsf path/to/country.rsf GB

    """ # NOQA


@record_group.command(name="list")
@click.option("--format", "output_format", type=click.Choice(["json", "csv"]))
@click.argument("rsf_file", type=click.Path(exists=False))
def list_command(rsf_file, output_format):
    """
    Computes the records for the given RSF_FILE.
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        records = register.records()

        if not records:
            return

        if output_format == "json":
            stream = StringIO()
            utils.serialise_json(records, stream)

            stream.seek(0)

            click.echo(stream.read())

        elif output_format == "csv":
            stream = StringIO()
            headers = Record.headers(register.schema())

            xsv.serialise(stream, records, headers)

            stream.seek(0)

            click.echo(stream.read())

        else:
            for record in records.values():
                click.echo(record.blob)

    except RegistersException as err:
        utils.error(str(err))


@record_group.command(name="show")
@click.option("--format", "output_format", type=click.Choice(["json", "csv"]))
@click.option("--rsf", "rsf_file", required=True,
              type=click.Path(exists=False))
@click.argument("key", type=click.Path(exists=False))
def show_command(key, rsf_file, output_format):
    """
    Computes the record for the given RSF_FILE and KEY.
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        records = register.records()

        if not records:
            return

        record = records.get(key)

        if not record:
            return

        if output_format == "json":
            stream = StringIO()
            utils.serialise_json(record, stream)

            stream.seek(0)

            click.echo(stream.read())

        elif output_format == "csv":
            stream = StringIO()
            headers = Record.headers(register.schema())

            xsv.serialise(stream, record, headers)

            stream.seek(0)

            click.echo(stream.read())

        else:
            for (attr, value) in record.blob:
                click.secho(f"{attr}:", fg="bright_yellow")
                click.echo(f"    {value}")

    except RegistersException as err:
        utils.error(str(err))
