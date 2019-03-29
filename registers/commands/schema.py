# -*- coding: utf-8 -*-

"""
This module implements the schema group of commands.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import csv
from datetime import datetime
from typing import List
from io import StringIO
import click
from .. import rsf, Register, Entry, Scope, Blob, Patch, Attribute
from ..exceptions import RegistersException, UnknownAttribute
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

            click.echo(stream.read())

        else:
            for attr in schema.attributes:
                is_primary_key = attr.uid == schema.primary_key
                display_attr(attr, is_primary_key)

    except RegistersException as err:
        utils.error(str(err))


@schema_group.command(name="patch")
@click.argument("attr_id")
@click.argument("value")
@click.option("--timestamp", default=format_timestamp(datetime.utcnow()),
              help=("A timestamp (RFC3339) to set for all entries in the "
                    "patch."))
@click.option("--rsf", "rsf_file", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
@click.option("--apply", "apply_flag", is_flag=True,
              help="Apply the patch to the given RSF file.")
def create_command(attr_id, value, rsf_file, timestamp, apply_flag):
    """
    Creates an RSF patch that modifies ATTR_ID description with the given
    VALUE.

    For example, to create a patch for the attribute ``name``:

        schema patch --rsf web-colors.rsf name "The W3C name of the colour."
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        cmds = patch_attr(attr_id, value, timestamp, register)

        if apply_flag:
            patch = Patch(register.schema(), cmds)
            register.apply(patch)

            with open(rsf_file, "a") as stream:
                stream.writelines([f"{cmd}\n" for cmd in patch.commands])

            msg = f"Appended {len(cmds)} changes to {rsf_file}"

            utils.success(msg)

        else:
            for obj in cmds:
                click.echo(obj)

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


def patch_attr(uid: str, value: str, timestamp: str,
               register: Register) -> List[rsf.Command]:
    """
    Composes the pair of RSF commands for an attribute patch.
    """

    attr = register.schema().get(uid)

    if attr is None:
        raise UnknownAttribute(uid, "foo")

    data = attr.to_dict()
    data["text"] = value

    blob = Blob(data)
    entry = Entry(f"field:{uid}", Scope.System, timestamp, blob.digest())

    return [rsf.add_item(blob), rsf.append_entry(entry)]
