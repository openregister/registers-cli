# -*- coding: utf-8 -*-

"""
This module implements the patch command group.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from datetime import datetime
import click
from .. import rsf, xsv, Register, Patch
from ..exceptions import RegistersException
from ..core import format_timestamp
from . import utils


@click.group(name="patch")
def patch_group():
    """
    Patch operations.
    """


@patch_group.command(name="create")
@click.argument("xsv_file")
@click.option("--timestamp", default=format_timestamp(datetime.utcnow()),
              help="A timestamp (RFC3339) to set for all entries in the \
patch.")
@click.option("--rsf", "rsf_file", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
@click.option("--apply", "apply_flag", is_flag=True,
              help="Apply the patch to the given RSF file.")
def create_command(xsv_file, rsf_file, timestamp, apply_flag):
    """
    Creates an RSF patch from XSV_FILE.

    XSV_FILE is expected to be either a TSV (Tab Separated Value) or a CSV
    (Comma Separated Value). The parser will try to determine the separator
    automatically.

    You must not use `;` as separator as it will conflict with cardinality 'n'
    value separator.
    """

    try:
        patch = create(xsv_file, rsf_file, timestamp,
                       apply_flag=apply_flag)

        if apply_flag:
            number = len(patch.commands)
            msg = f"Appended {number} changes to {rsf_file}"

            utils.success(msg)

        else:
            for command in patch.commands:
                click.echo(command)

    except RegistersException as err:
        utils.error(str(err))


@patch_group.command(name="apply")
@click.argument("patch_file")
@click.option("--rsf", "rsf_file", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
def apply_command(patch_file, rsf_file):
    """
    Applies PATCH_FILE to the given RSF file.
    """

    try:
        patch = apply(patch_file, rsf_file)
        number = len(patch.commands)
        msg = f"Appended {number} changes to {rsf_file}"

        utils.success(msg)

    except RegistersException as err:
        utils.error(str(err))


def create(xsv_file: str, rsf_file: str,
           timestamp: str, apply_flag: bool = False) -> Patch:
    """
    Creates an RSF patch.
    """

    cmds = rsf.read(rsf_file)
    register = Register(cmds)

    utils.check_readiness(register)

    schema = register.schema()

    with open(xsv_file, "r", newline="") as handle:
        blobs = xsv.deserialise(handle, schema)
        patch = Patch(schema, blobs, timestamp)

        errors = register.apply(patch)

        if errors:
            utils.error(errors)

        if apply_flag:
            return _apply(patch, rsf_file)

        return patch


def apply(patch_file: str, rsf_file: str) -> Patch:
    """
    Applies an RSF patch.
    """

    cmds = rsf.read(rsf_file)
    register = Register(cmds)

    utils.check_readiness(register)

    schema = register.schema()

    patch_cmds = rsf.read(patch_file)
    patch = Patch(schema, patch_cmds)
    errors = register.apply(patch)

    if errors:
        utils.error(errors)

    return _apply(patch, rsf_file)


def _apply(patch: Patch, rsf_file: str) -> Patch:
    """
    Applies a patch and saves RSF to the given file.
    """

    with open(rsf_file, "a") as handle:
        handle.writelines([f"{cmd}\n" for cmd in patch.commands])

    return patch
