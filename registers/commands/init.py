# -*- coding: utf-8 -*-

"""
This module implements the init command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import os
from hashlib import sha256
from datetime import datetime
from typing import List
import click
from . import utils
from .. import (rsf, schema, merkle, Hash, Blob, Entry, Scope,
                Attribute, Datatype, Cardinality)
from ..core import format_timestamp
from ..exceptions import RegistersException


@click.command(name="init")
@click.argument("name")
@click.option("--rsf", "rsf_file", required=True,
              type=click.Path(exists=False),
              help=("The RSF file that will be created as a result of the "
                    "command"))
def init_command(name, rsf_file):
    """
    Creates a new register with the given NAME to the given RSF file.
    """

    if os.path.exists(rsf_file):
        raise click.UsageError("Please select a file that does not exist.")

    try:
        commands = init_patch(name)

        with click.open_file(rsf_file, "w", "utf-8") as stream:
            stream.write(rsf.dump(commands))

        fname = click.style(click.format_filename(rsf_file),
                            fg='bright_yellow')
        click.echo(f"Empty register successfully created at {fname}")

    except RegistersException as err:
        utils.error(str(err))


def init_patch(name: str) -> List[rsf.Command]:
    """
    Creates the initial set of commands from a given name (register uid).
    """

    timestamp = format_timestamp(datetime.utcnow())

    uid = Blob({"name": name})
    uid_entry = Entry("name", Scope.System, timestamp,
                      uid.digest())

    commands = [
        rsf.assert_root_hash(Hash("sha-256", merkle.hash_empty(sha256).hex())),

        rsf.add_item(uid),
        rsf.append_entry(uid_entry),
    ]

    attributes = gather_attributes(name, timestamp)

    commands.extend(attributes)

    return commands


def gather_attributes(name: str, timestamp: str) -> List[rsf.Command]:
    """
    Gathers attribute information from the user.
    """

    cmds = []

    primary_key = schema.string(name).to_blob()
    primary_key_entry = Entry(f"field:{name}", Scope.System, timestamp,
                              primary_key.digest())

    cmds.append(rsf.add_item(primary_key))
    cmds.append(rsf.append_entry(primary_key_entry))

    click.echo(f"Primary key {name} added.")

    while True:
        if click.confirm("Do you want to add an attribute?"):
            uid = click.prompt("Id:", type=str)
            datatype = click.prompt("Datatype:",
                                    type=click.Choice(schema.DATATYPES))
            cardinality = click.prompt("Cardinality:",
                                       type=click.Choice(["1", "n"]))
            description = click.prompt("Description:", type=str)

            attr = Attribute(uid,
                             Datatype(datatype),
                             Cardinality(cardinality),
                             description)
            blob = attr.to_blob()
            entry = Entry(f"field:{uid}", Scope.System, timestamp,
                          blob.digest())
            cmds.append(rsf.add_item(blob))
            cmds.append(rsf.append_entry(entry))
        else:
            break

    return cmds
