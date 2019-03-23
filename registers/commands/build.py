# -*- coding: utf-8 -*-

"""
This module implements the build command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import csv
import shutil
from pathlib import Path
import click
from .. import rsf, xsv, Register
from ..exceptions import RegistersException
from . import utils
from .utils import error


@click.command(name="build")
@click.argument("rsf_file", type=click.Path(exists=True))
def build_command(rsf_file):
    """
    Builds the static version of the register. Derives all required files such
    that a static web server conforms to the REST API specification (V1).
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        build_path = Path(f"build/{register.uid}")

        if build_path.exists():
            shutil.rmtree(build_path)

        build_path.mkdir(parents=True)

        blobs_path = build_path.joinpath("items")
        entries_path = build_path.joinpath("entries")
        records_path = build_path.joinpath("records")

        build_blobs(blobs_path, register)
        build_entries(entries_path, register)
        build_records(records_path, register)

        click.secho("Build complete.", fg="green", bold=True)

    except RegistersException as err:
        error(str(err))


def build_blobs(path: Path, register: Register):
    """
    Generates all blob files.
    """

    if path.exists():
        path.rmdir()

    path.mkdir()

    sch = register.schema()
    headers = [attr.uid for attr in sch.attributes]
    collection = register.log.blobs

    write_json_resource(path.joinpath("index"),
                        {repr(k): v for k, v in collection.items()})

    with open(f"{path}/index.csv", "w") as stream_collection:
        writer = csv.writer(stream_collection)
        writer.writerow(headers)

        with utils.progressbar(collection.items(),
                               label='Building blobs') as bar:

            for key, blob in bar:
                row = xsv.serialise_object(blob, headers=headers)
                writer.writerow(row)

                write_resource(path.joinpath(repr(key)), blob, headers)


def build_entries(path: Path, register: Register):
    """
    Generates all entry files.
    """

    if path.exists():
        path.rmdir()

    path.mkdir()

    headers = ["index-entry-number",
               "entry-number",
               "entry-timestamp",
               "key",
               "item-hash"]
    collection = register.log.entries

    write_json_resource(path.joinpath("index"), collection)

    with open(f"{path}/index.csv", "w") as stream_collection:
        writer = csv.writer(stream_collection)
        writer.writerow(headers)

        with utils.progressbar(collection, label='Building entries') as bar:
            for entry in bar:
                row = xsv.serialise_object(entry)
                writer.writerow(row)

                write_resource(path.joinpath(repr(entry.position)),
                               entry, headers)


def build_records(path: Path, register: Register):
    """
    Generates all record files.
    """

    if path.exists():
        path.rmdir()

    path.mkdir()

    sch = register.schema()
    headers = ["index-entry-number",
               "entry-number",
               "entry-timestamp",
               "key"]
    blob_headers = [attr.uid for attr in sch.attributes]
    headers.extend(blob_headers)

    collection = register.records()

    write_json_resource(path.joinpath("index"), collection)

    with open(f"{path}/index.csv", "w") as stream_collection:
        writer = csv.writer(stream_collection)
        writer.writerow(headers)

        with utils.progressbar(collection.items(),
                               label='Building records') as bar:
            for key, record in bar:
                row = xsv.serialise_object(record, blob_headers)
                writer.writerow(row)

                write_resource(path.joinpath(key), record, headers,
                               blob_headers)


def write_resource(path: Path, obj, headers, blob_headers=None):
    """
    Generates the pair of files (csv, json) for the given object.
    """

    if blob_headers:
        row = xsv.serialise_object(obj, headers=blob_headers)
    else:
        row = xsv.serialise_object(obj, headers=headers)

    with open(f"{path}.csv", "w") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerow(row)

    write_json_resource(path, obj)


def write_json_resource(path: Path, obj):
    """
    Writes the given object to a file as JSON.
    """

    with open(f"{path}.json", "w") as stream:
        utils.serialise_json(obj, stream)
