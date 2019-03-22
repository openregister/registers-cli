import click
import json
import os.path
import io
from datetime import datetime
from .core import EMPTY_ROOT_HASH, __version__, format_timestamp
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
    pass


cli.add_command(commands.build_command)


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
@click.argument("rsf_file", type=click.Path(exists=False))
@click.option("--format", "output_format", type=click.Choice(["json"]))
def context(rsf_file, output_format):
    """Computes the context for the given RSF file."""
    try:
        cmds = rsf.read(rsf_file)
        r = Register(cmds)

        commands.utils.check_readiness(r)

        context = r.context()

        if output_format == "json":
            click.echo(json.dumps(context))

        else:
            click.secho("custodian:", fg="yellow", bold=True)
            click.echo(f"    {context['custodian']}\n")
            click.secho("last update:", fg="yellow", bold=True)
            click.echo(f"    {context['last-updated']}\n")
            click.secho("total records:", fg="yellow", bold=True)
            click.echo(f"    {context['total-records']}\n")
            click.secho("total entries:", fg="yellow", bold=True)
            click.echo(f"    {context['total-entries']}\n")

    except RegistersException as e:
        error(str(e))


@cli.command()
@click.argument("rsf_file", type=click.Path(exists=False))
def records(rsf_file):
    """Computes the records for the given RSF file."""
    try:
        cmds = rsf.read(rsf_file)
        r = Register(cmds)

        commands.utils.check_readiness(r)

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


@blob.command(name="list")
@click.option("--format", "output_format", type=click.Choice(["json", "csv"]))
@click.option("--rsf", "rsf_path", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
@click.option("--output", "output_filename",
              help="The filename to write the result.")
def list_blobs(rsf_path, output_format, output_filename):
    try:
        if output_format == "csv":
            if output_filename is None:
                stream = io.StringIO()
                result = commands.blob.list(rsf_path, output_format, stream)

                for row in stream:
                    click.echo(row[:-1])
            else:
                with open(output_filename, "w") as stream:
                    commands.blob.list(rsf_path, output_format, stream)

        elif output_format == "json":
            if output_filename is None:
                stream = io.StringIO()
                result = commands.blob.ls(rsf_path, output_format, stream)

                click.echo(stream.read())

            else:
                with open(output_filename, "w") as stream:
                    commands.blob.ls(rsf_path, output_format, stream)

        else:
            result = commands.blob.ls(rsf_path)

            for blob in result:
                click.echo(repr(blob))

    except RegistersException as e:
        error(str(e))


@blob.command(name="validate")
@click.argument("blob")
@click.option("--rsf", "rsf_path", required=True, type=click.Path(exists=True),
              help="An RSF file with valid metadata")
def validate_blob(blob, rsf_path):
    try:
        result = commands.blob.validate(blob, rsf_path)
        blob = result["blob"]
        register = result["register"]

        msg = f"'{blob}' is valid for the '{register.uid}' register."

        click.secho(msg, fg="green", bold=True)

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
