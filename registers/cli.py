import click
import json
import os.path

from .core import EMPTY_ROOT_HASH, __version__
from . import rsf, Register, validator, Datatype, Blob
from .exceptions import RegistersException


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
    pass


@cli.command()
@click.argument("filepath", type=click.Path(exists=False))
def init(filepath):
    """Creates an empty register."""
    assert_root_hash = f"assert-root-hash\t{EMPTY_ROOT_HASH}"

    if os.path.exists(filepath):
        raise click.UsageError("Please select a file that does not exist.")

    with click.open_file(filepath, "w", "utf-8") as handle:
        handle.write(assert_root_hash)

    fname = click.style(click.format_filename(filepath), fg='bright_yellow')
    click.echo(f"Empty register successfully created at {fname}")


@cli.command()
@click.argument("filepath", type=click.Path(exists=False))
def records(filepath):
    """Computes the records for the given RSF file."""
    try:
        cmds = rsf.read(filepath)
        r = Register()
        r.load_commands(cmds)

        if not r.is_ready():
            error("The given RSF does not have enough information to be used \
in this command.")

        records = r.records()

        for blob in records.values():
            click.echo(blob)

    except RegistersException as e:
        error(str(e))


@cli.group()
def blob():
    """
    Blob operations.

    For example, you can validate that a blob '{"country": "ZZ", "name": "Zeta"}'
    conforms to the schema defined in the country register in RSF:

        blob validate --rsf path/to/country.rsf '{"country": "ZZ", "name": "Zeta"}'
    """ # NOQA


@blob.command()
@click.argument("blob")
@click.option("--rsf", "rsf_path", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
def validate(blob, rsf_path):
    try:
        cmds = rsf.read(rsf_path)
        r = Register()
        r.load_commands(cmds)

        if not r.is_ready():
            error("The given RSF does not have enough information to be used \
in this command.")

        schema = r.schema()

        data = json.loads(blob)
        validator.validate(data, schema)

        click.secho(f"'{Blob(data)}' is valid for the '{r.uid}' register.",
                    fg="green", bold=True)
    except json.decoder.JSONDecodeError:
        error("The given blob is not well formed JSON.")

    except RegistersException as e:
        error(str(e))


@cli.group()
def value():
    """
    Value operations.

    For example, you can validate a token 'P2Y' conforms to a 'period' datatype
    by using `value validate --type period P2Y`.
    """


@value.command() # NOQA
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
def validate(token, datatype):
    try:
        validator.validate_value_datatype(token, Datatype(datatype))

        click.secho(f"'{token}' is a valid '{datatype}'.", fg="green",
                    bold=True)

    except RegistersException as e:
        error(str(e))
