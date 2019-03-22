import click
import json
import csv
import shutil
from pathlib import Path
from .. import rsf, xsv, Register
from ..exceptions import RegistersException
from . import utils
from .utils import error


@click.command(name="build")
@click.argument("rsf_filename", type=click.Path(exists=True))
def build_command(rsf_filename):
    """
    Builds the static version of the register. Derives all required files such
    that a static web server conforms to the REST API specification (V1).
    """
    try:
        build_path = Path("build")

        if build_path.exists():
            shutil.rmtree(build_path)

        build_path.mkdir()

        blobs_path = build_path.joinpath("items")
        # entries_path = build_path.joinpath("entries")
        # records_path = build_path.joinpath("records")

        cmds = rsf.read(rsf_filename)
        register = Register(cmds)

        utils.check_readiness(register)
        build_blobs(blobs_path, register)

        click.secho("Build complete.", fg="green", bold=True)

    except RegistersException as e:
        error(str(e))


def build_blobs(path: Path, register: Register):
    if path.exists():
        path.rmdir()

    path.mkdir()

    sch = register.schema()
    headers = [attr.uid for attr in sch.attributes]
    collection = register.log.blobs

    with open(f"{path}.json", "w") as stream_collection:
        utils.serialise_json({repr(k): v for k, v in collection.items()},
                             stream_collection)

    with open(f"{path}.csv", "w") as stream_collection:
        writer = csv.writer(stream_collection)
        writer.writerow(headers)

        with utils.progressbar(collection.items(),
                               label='Building blobs') as bar:

            for key, blob in bar:
                row = xsv.serialise_object(blob, headers=headers)
                writer.writerow(row)

                write_resource(path.joinpath(repr(key)), blob, headers)


def write_resource(path: Path, obj, headers):
    row = xsv.serialise_object(obj, headers=headers)

    with open(f"{path}.csv", "w") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerow(row)

    with open(f"{path}.json", "w") as stream:
        stream.write(repr(obj))
