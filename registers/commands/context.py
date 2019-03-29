# -*- coding: utf-8 -*-

"""
This module implements the context group of commands.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import csv
import json
from datetime import datetime
from typing import List, cast
from io import StringIO
import click
from .. import rsf, Register, Entry, Scope, Blob, Patch, Record
from ..exceptions import RegistersException
from ..core import format_timestamp
from . import utils


@click.group(name="context")
def context_group():
    """
    Context operations.
    """


@context_group.command(name="show")
@click.argument("rsf_file", type=click.Path(exists=False))
@click.option("--format", "output_format", type=click.Choice(["json", "csv"]))
def show_command(rsf_file, output_format):
    """
    Shows the context for the given RSF_FILE.
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        context = register.context()

        if output_format == "json":
            click.echo(json.dumps(context))

        else:
            context["register"] = register.uid
            context["fields"] = ";".join(context["register-record"]["fields"])
            context["registry"] = context["register-record"]["registry"]

            del context["register-record"]

            if output_format == "csv":
                stream = StringIO()

                writer = csv.DictWriter(stream, fieldnames=context.keys())
                writer.writeheader()
                writer.writerow(context)

                stream.seek(0)

                for row in stream:
                    click.echo(row[:-1])

            else:
                for key, value in context.items():
                    click.secho(f"{key}:", fg="yellow", bold=True)
                    click.echo(f"    {value}\n")

    except RegistersException as err:
        utils.error(str(err))


@context_group.command(name="patch")
@click.argument("key", type=click.Choice(["custodian",
                                          "title",
                                          "description"]))
@click.argument("value")
@click.option("--timestamp", default=format_timestamp(datetime.utcnow()),
              help=("A timestamp (RFC3339) to set for all entries in the "
                    "patch."))
@click.option("--rsf", "rsf_file", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
@click.option("--apply", "apply_flag", is_flag=True,
              help="Apply the patch to the given RSF file.")
def create_command(key, value, rsf_file, timestamp, apply_flag):
    """
    Creates an RSF patch from VALUE for the given KEY.

    For example, to create a patch for the custodian:

        context patch --rsf web-colors.rsf custodian "John Doe"

    To create a patch for changing the registers title:

        context patch --rsf web-colors.rsf title "The Web Colour Register"
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        patch = create_patch(key, value, timestamp, register)

        if apply_flag:
            register.apply(patch)

            with open(rsf_file, "a") as stream:
                stream.writelines([f"{cmd}\n" for cmd in patch.commands])

            msg = f"Appended {len(cmds)} changes to {rsf_file}"

            utils.success(msg)

        else:
            for obj in patch.commands:
                click.echo(obj)

    except RegistersException as err:
        utils.error(str(err))


def create_patch(key, value, timestamp, register):
    """
    Creates an RSF context patch.
    """

    if key == "custodian":
        cmds = context_patch("custodian", value, timestamp)

    elif key == "title":
        cmds = context_patch("register-name", value, timestamp)

    elif key == "description":
        cmds = description_patch(value, timestamp, register)

    else:
        raise RegistersException(
            f"A context patch for {key} can't be created.")

    return Patch(register.schema(), cmds)


def description_patch(value: str, timestamp: str,
                      register: Register) -> List[rsf.Command]:
    """
    Composes the pair of RSF commands for a description patch.
    """

    key = f"register:{register.uid}"
    data = cast(Record, register.metalog.find(key)).blob.to_dict()
    data["text"] = value

    blob = Blob(data)
    entry = Entry(key, Scope.System, timestamp, blob.digest())

    return [rsf.add_item(blob), rsf.append_entry(entry)]


def context_patch(key: str, value: str, timestamp: str) -> List[rsf.Command]:
    """
    Composes the pair of RSF commands for a context patch.
    """

    blob = Blob({key: value})
    entry = Entry(key, Scope.System, timestamp, blob.digest())

    return [rsf.add_item(blob), rsf.append_entry(entry)]
