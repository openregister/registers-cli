# -*- coding: utf-8 -*-

"""
This module implements the context command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import csv
import json
from io import StringIO
import click
from .. import rsf, Register
from ..exceptions import RegistersException
from . import utils


@click.command(name="context")
@click.argument("rsf_file", type=click.Path(exists=False))
@click.option("--format", "output_format", type=click.Choice(["json", "csv"]))
def context_command(rsf_file, output_format):
    """
    Computes the context for the given RSF_FILE.
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        context = register.context()

        if output_format == "json":
            click.echo(json.dumps(context))

        else:
            context["fields"] = ";".join(context["register-record"]["fields"])
            context["register"] = context["register-record"]["register"]
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
