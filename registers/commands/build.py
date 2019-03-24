# -*- coding: utf-8 -*-

"""
This module implements the build command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import csv
import shutil
from pathlib import Path
from typing import List, Dict
import click
from .. import rsf, xsv, Register, Entry, Record
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

    write_resource(path.joinpath("index"),
                   {repr(k): v for k, v in collection.items()},
                   headers)

    with utils.progressbar(collection.items(),
                           label='Building blobs') as bar:

        for key, blob in bar:
            write_resource(path.joinpath(repr(key)), blob, headers)


def build_entries(path: Path, register: Register):
    """
    Generates all entry files.
    """

    if path.exists():
        path.rmdir()

    path.mkdir()

    headers = Entry.headers()
    collection = register.log.entries

    write_resource(path.joinpath("index"), collection, headers)

    with utils.progressbar(collection, label='Building entries') as bar:
        for entry in bar:
            write_resource(path.joinpath(repr(entry.position)), entry, headers)


def build_records(path: Path, register: Register):
    """
    Generates all record files.
    """

    if path.exists():
        path.rmdir()

    path.mkdir()

    sch = register.schema()
    headers = Record.headers(sch)
    collection = register.records()

    write_resource(path.joinpath("index"), collection, headers)

    with utils.progressbar(collection.items(),
                           label='Building records') as bar:
        for key, record in bar:
            write_resource(path.joinpath(key), record, headers)

            build_record_trail(path.joinpath(key), register.trail(key))


def build_record_trail(path: Path, trail: List[Entry]):
    """
    Generates the record trail.
    """

    if path.exists():
        path.rmdir()

    path.mkdir()
    path = path.joinpath("entries")

    write_resource(path, trail, headers=Entry.headers())


def write_resource(path: Path, obj, headers):
    """
    Generates the pair of files (csv, json) for the given object.
    """

    write_csv_resource(path, obj, headers)
    write_json_resource(path, obj)


def write_csv_resource(path: Path, obj, headers):
    """
    Writes the given object to a file as CSV.
    """

    with open(f"{path}.csv", "w") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)

        if isinstance(obj, List):
            for element in obj:
                row = xsv.serialise_object(element, headers=headers)
                writer.writerow(row)

        elif isinstance(obj, Dict):
            for element in obj.values():
                row = xsv.serialise_object(element, headers=headers)
                writer.writerow(row)

        else:
            row = xsv.serialise_object(obj, headers=headers)
            writer.writerow(row)


def write_json_resource(path: Path, obj):
    """
    Writes the given object to a file as JSON.
    """

    with open(f"{path}.json", "w") as stream:
        utils.serialise_json(obj, stream)
