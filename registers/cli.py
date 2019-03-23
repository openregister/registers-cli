import click
import json
import os.path
import io
from datetime import datetime
from .core import __version__, format_timestamp
from . import rsf, Register, validator, Datatype
from .exceptions import RegistersException
from . import commands


def error(message):
    """
    Sends a message to stderr and exits with code error 1.
    """

    click.secho(message, fg="red", bold=True, err=True)
    exit(1)


@click.group()
@click.version_option(prog_name=click.style("registers", fg='bright_yellow'),
                      version=__version__)
def cli():
    """
    registers lets you manage a Register represented as a Register
    Serialisation Format (RSF).
    """


cli.add_command(commands.init_command)
cli.add_command(commands.build_command)
cli.add_command(commands.context_command)
cli.add_command(commands.records_command)
cli.add_command(commands.blob_group)


@cli.group()
def value():
    """
    Value operations.

    For example, you can validate a token 'P2Y' conforms to a 'period' datatype
    by using `value validate --type period P2Y`.
    """


@value.command(name="validate")
@click.argument("token")
@click.option("--type", "datatype", required=True,
              type=click.Choice(["curie",
                                 "datetime",
                                 "name",
                                 "hash",
                                 "integer",
                                 "period",
                                 "string",
                                 "text",
                                 "timestamp",
                                 "url"]),
              help="The datatype TOKEN is expected to conform to.")
def validate_value(token, datatype):
    try:
        validator.validate_value_datatype(token, Datatype(datatype))

        msg = f"'{token}' is a valid '{datatype}'."

        click.secho(msg, fg="green", bold=True)

    except RegistersException as e:
        error(str(e))


@cli.group()
def patch():
    """
    Patch operations.
    """


@patch.command()
@click.argument("xsv_file")
@click.option("--timestamp", default=format_timestamp(datetime.utcnow()),
              help="A timestamp (RFC3339) to set for all entries in the \
patch.")
@click.option("--rsf", "rsf_file", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
@click.option("--apply", "apply_flag", is_flag=True,
              help="Apply the patch to the given RSF file.")
def create(xsv_file, rsf_file, timestamp, apply_flag):
    """
    Creates an RSF patch from XSV_FILE.

    XSV_FILE is expected to be either a TSV (Tab Separated Value) or a CSV
    (Comma Separated Value). The parser will try to determine the separator
    automatically.

    You must not use `;` as separator as it will conflict with cardinality 'n'
    value separator.
    """
    try:
        result = commands.patch.create(xsv_file, rsf_file, timestamp,
                                       apply_flag=apply_flag)

        if apply_flag:
            n = result['added_commands_number']
            msg = f"Appended {n} changes to {rsf_file}"

            click.secho(msg, fg="green", bold=True)

        else:
            for obj in result:
                click.echo(obj)

    except RegistersException as e:
        error(str(e))


@patch.command()
@click.argument("patch_file")
@click.option("--rsf", "rsf_file", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
def apply(patch_file, rsf_file):
    """
    Applies PATCH_FILE to the given RSF_FILE.
    """
    try:
        result = commands.patch.apply(patch_file, rsf_file)
        n = result['added_commands_number']
        msg = f"Appended {n} changes to {rsf_file}"

        click.secho(msg, fg="green", bold=True)

    except RegistersException as e:
        error(str(e))
