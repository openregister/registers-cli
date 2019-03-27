# -*- coding: utf-8 -*-

"""
This module implements the context command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import csv
from datetime import datetime
from typing import List, cast
from io import StringIO
import click
from .. import rsf, Register, Entry, Scope, Blob, Patch, Record, Attribute
from ..exceptions import RegistersException
from ..core import format_timestamp
from . import utils


@click.group(name="schema")
def schema_group():
    """
    Schema operations.
    """


@schema_group.command(name="show")
@click.argument("rsf_file", type=click.Path(exists=False))
@click.option("--format", "output_format", type=click.Choice(["json", "csv"]))
def show_command(rsf_file, output_format):
    """
    Shows the schema for the given RSF_FILE.
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        schema = register.schema()

        if output_format == "json":
            stream = StringIO()
            utils.serialise_json(schema, stream)
            stream.seek(0)
            click.echo(stream.read())

        elif output_format == "csv":
            stream = StringIO()
            headers = Attribute.headers()
            headers.append("primary_key")

            writer = csv.DictWriter(stream, fieldnames=headers)
            writer.writeheader()

            attributes = schema.attributes

            for attr in attributes:
                data = attr.to_dict()
                data["primary_key"] = str(attr.uid ==
                                          schema.primary_key).lower()
                writer.writerow(data)

            stream.seek(0)

            for row in stream:
                click.echo(row[:-1])

        else:
            for attr in schema.attributes:
                is_primary_key = attr.uid == schema.primary_key
                display_attr(attr, is_primary_key)

    except RegistersException as err:
        utils.error(str(err))


def display_attr(attr: Attribute, is_primary_key: bool):
    """
    Displays the attribute to STDOUT.
    """

    if is_primary_key:
        pk_label = " (primary key)"
    else:
        pk_label = ""

    click.secho(f"{attr.uid}{pk_label}", fg="bright_yellow")

    for (key, value) in [(key, value) for key, value in attr
                         if key != "field"]:
        svalue = click.style(value, fg="white")
        click.secho(f"    {key}: {svalue}", fg="bright_white")
