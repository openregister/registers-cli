# -*- coding: utf-8 -*-

"""
This module implements the build command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import shutil
from zipfile import ZipFile
from pathlib import Path
from typing import List
import click
from .. import rsf, log, Register, Entry, Record
from ..exceptions import RegistersException
from . import utils
from .utils import error


@click.command(name="build")
@click.argument("rsf_file", type=click.Path(exists=True))
def build_command(rsf_file):
    """
    Builds the static version of the register. Derives all required files such
    that a static web server conforms to the REST API specification (V1).

    The expected result for a register named ``web-colours``:

        \b
        build
        └── web-colours
            ├── archive.zip
            ├── commands
            │  ├── 0.rsf
            │  ├── 1.rsf
            .  .
            .  .
            ├── entries
            │  ├── 1.rsf
            │  ├── 2.rsf
            .  .
            .  .
            ├── items
            │  ├── sha-256:cc524b28...b22dc1f27ed35da34564.csv
            │  ├── sha-256:cc524b28...b22dc1f27ed35da34564.json
            .  .
            .  .
            ├── records
            .  .
            .  .
            │  ├── purple.csv
            │  ├── purple.json
            │  ├── purple
            │  │  ├── entries.csv
            │  │  └── entries.json
            │  ├── index.csv
            │  └── index.json
            └── register.json

    Note that the name of the file RSF_FILE is not used for any part of the
    build process.
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
        commands_path = build_path.joinpath("commands")
        context_path = build_path.joinpath("register")

        build_blobs(blobs_path, register)
        build_entries(entries_path, register)
        build_records(records_path, register)
        build_commands(commands_path, register)
        build_context(context_path, register)
        build_archive(build_path, register)

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
            write_resource(path.joinpath(repr(entry.position)),
                           [entry], headers)

    build_entry_slices(path.joinpath("slices"), register)


def build_entry_slices(path: Path, register: Register):
    """
    Generates all entry slice files.
    """

    if path.exists():
        path.rmdir()

    path.mkdir()

    headers = Entry.headers()

    with utils.progressbar(range(0, register.log.size),
                           label='Building entry slices') as bar:
        for idx in bar:
            write_resource(path.joinpath(str(idx + 1)),
                           register.log.entries[idx:],
                           headers)


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


def build_commands(path: Path, register: Register):
    """
    Generates all RSF files.
    """

    if path.exists():
        path.rmdir()

    path.mkdir()

    with open(f"{path}/0.rsf", "w") as stream:
        stream.write(rsf.dump(register.commands))

    with utils.progressbar(range(1, register.log.size),
                           label='Building commands') as bar:
        for idx in bar:
            commands = log.slice(register.log, idx)

            with open(f"{path}/{idx}.rsf", "w") as stream:
                stream.write(rsf.dump(commands))


def build_context(path: Path, register: Register):
    """
    Generates context files.
    """

    context = register.context()

    utils.write_json_resource(path, context)


def build_archive(path: Path, register: Register):
    """
    Generates archive (zip) file.
    """

    with ZipFile(f"{path}/archive.zip", "w") as archive:
        archive.write(f"build/{register.uid}/items/index.json",
                      f"{register.uid}/item/index.json")
        archive.write(f"build/{register.uid}/entries/index.json",
                      f"{register.uid}/entry/index.json")
        archive.write(f"build/{register.uid}/records/index.json",
                      f"{register.uid}/record/index.json")
        archive.write(f"build/{register.uid}/register.json",
                      f"{register.uid}/register.json")


def write_resource(path: Path, obj, headers):
    """
    Generates the pair of files (csv, json) for the given object.
    """

    utils.write_csv_resource(path, obj, headers)
    utils.write_json_resource(path, obj)
