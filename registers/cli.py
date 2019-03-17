import click
import json
import os.path

from .core import EMPTY_ROOT_HASH, __version__
from . import rsf, Register, validator
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


@cli.group()
def blob():
    pass


@blob.command()
@click.argument("blob")
@click.option("--rsf", "rsf_path", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
def validate(blob, rsf_path):
    try:
        cmds = rsf.read(rsf_path)
        r = Register()
        r.load_commands(cmds)
        schema = r.schema()

        data = json.loads(blob)
        validator.validate(data, schema)

        click.secho(f"The given blob '{blob}' is valid.", fg="green",
                    bold=True)
    except json.decoder.JSONDecodeError:
        error("The given blob is not well formed JSON.")

    except RegistersException as e:
        error(str(e))
