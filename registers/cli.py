import click
import os.path

from .core import EMPTY_ROOT_HASH, __version__


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
