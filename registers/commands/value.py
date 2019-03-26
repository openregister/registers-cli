# -*- coding: utf-8 -*-

"""
This module implements the value command group.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import click
from .. import validator, schema, Datatype
from ..exceptions import RegistersException
from . import utils


@click.group(name="value")
def value_group():
    """
    Value operations.

    For example, you can validate a token 'P2Y' conforms to a 'period' datatype
    by using `value validate --type period P2Y`.
    """


@value_group.command(name="validate")
@click.argument("token")
@click.option("--type", "datatype", required=True,
              type=click.Choice(schema.DATATYPES),
              help="The datatype TOKEN is expected to conform to.")
def validate_command(token, datatype):
    """
    Validates a value against the given datatype.
    """

    try:
        validator.validate_value_datatype(token, Datatype(datatype))

        msg = f"'{token}' is a valid '{datatype}'."

        utils.success(msg)

    except RegistersException as err:
        utils.error(str(err))
