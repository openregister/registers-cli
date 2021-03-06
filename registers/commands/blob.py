# -*- coding: utf-8 -*-

"""
This module implements the blob command group.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import json
from io import StringIO
import click
from .. import rsf, xsv, Register, Blob, validator
from ..exceptions import RegistersException
from . import utils


@click.group(name="blob")
def blob_group():
    """
    Blob operations.

    For example, you can validate that a blob '{"country": "ZZ", "name": "Zeta"}'
    conforms to the schema defined in the country register in RSF:

        blob validate --rsf path/to/country.rsf '{"country": "ZZ", "name": "Zeta"}'
    """ # NOQA


@blob_group.command(name="list")
@click.argument("rsf_file", type=click.Path(exists=True))
@click.option("--format", "output_format", type=click.Choice(["json", "csv"]))
def list_command(rsf_file, output_format):
    """
    Lists the blobs found in the given RSF_FILE.
    """

    try:
        if output_format:
            stream = StringIO()
            list_blobs(rsf_file, output_format, stream)

            click.echo(stream.read())

        else:
            result = list_blobs(rsf_file)

            for blob in result:
                click.echo(repr(blob))

    except RegistersException as err:
        utils.error(str(err))


@blob_group.command(name="validate")
@click.argument("blob")
@click.option("--rsf", "rsf_file", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
def validate_blob(blob, rsf_file):
    """
    Validates the given json BLOB against the schema derived from the given
    RSF file.
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        schema = register.schema()

        data = json.loads(blob)
        validator.validate(data, schema)

        blob = Blob(data)

        msg = f"'{blob}' is valid for the '{register.uid}' register."

        utils.success(msg)

    except json.decoder.JSONDecodeError:
        utils.error("The given blob is not well formed JSON.")

    except RegistersException as err:
        utils.error(str(err))


def list_blobs(rsf_file, output_format=None, stream=None):
    """
    Lists the blobs found in the RSF file.
    """

    cmds = rsf.read(rsf_file)
    register = Register(cmds)

    utils.check_readiness(register)
    blobs = register.log.blobs

    if output_format == "csv":
        schema = register.schema()
        headers = [attr.uid for attr in schema.attributes]
        xsv.serialise(stream, blobs, headers)

        stream.seek(0)

        return None

    if output_format == "json":
        utils.serialise_json({repr(k): v for k, v in blobs.items()}, stream)

        stream.seek(0)

        return None

    return blobs.values()
