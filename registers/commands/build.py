# -*- coding: utf-8 -*-

"""
This module implements the build command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import json
import yaml
import shutil
from zipfile import ZipFile
from pathlib import Path
from typing import List, Union, Dict
import pkg_resources
import click
from .. import rsf, log, Register, Entry, Record, Cardinality
from ..exceptions import RegistersException
from . import utils
from .utils import error


@click.command(name="build")
@click.argument("rsf_file", type=click.Path(exists=True))
@click.option("--target", type=click.Choice(["netlify", "cloudfoundry"]),
              help="Publication target")
def build_command(rsf_file, target):
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

    Publication target
    ==================

    If the publication target `--target` is specified it will generate the
    appropriate rewrite and redirect rules such that the API behaves as close
    as possible to the original reference implementation.
    """

    try:
        cmds = rsf.read(rsf_file)
        register = Register(cmds)

        utils.check_readiness(register)

        build_path = Path(f"build/{register.uid}")

        if build_path.exists():
            shutil.rmtree(build_path)

        build_path.mkdir(parents=True)

        if target == "netlify":
            with open(build_path.joinpath("_redirects"), "wb") as handle:
                handle.write(pkg_resources.resource_string("registers",
                                                           "data/_redirects"))
        if target == "cloudfoundry":
            build_cloudfoundry(build_path, register)
            build_path = build_path.joinpath("public")
            build_path.mkdir()

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

        build_openapi(build_path, register)

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
    Generates the archive (zip) file.
    """

    with ZipFile(f"{path}/archive.zip", "w") as archive:
        archive.write(f"{path}/items/index.json",
                      f"{register.uid}/item/index.json")
        archive.write(f"{path}/entries/index.json",
                      f"{register.uid}/entry/index.json")
        archive.write(f"{path}/records/index.json",
                      f"{register.uid}/record/index.json")
        archive.write(f"{path}/register.json",
                      f"{register.uid}/register.json")


def build_openapi(path: Path, register: Register):
    """
    Generates the openapi file.
    """

    openapi = json.loads(pkg_resources.resource_string("registers", "data/openapi.json"))  # NOQA

    openapi["info"]["title"] = register.title() or register.uid

    if register.description():
        openapi["info"]["description"] = register.description()

    item_props = {}

    for attribute in register.schema().attributes:
        item_props[attribute.uid] = _attr_schema(attribute)

    openapi["components"]["schemas"]["Item"]["properties"] = item_props

    with open(path.joinpath("openapi.json"), "w") as handle:
        handle.write(json.dumps(openapi))


def build_cloudfoundry(path: Path, register: Register):
    static_config_files = ["buildpack.yml", "mime.types", "nginx.conf"]
    for filename in static_config_files:
        cf_path = f"data/cloudfoundry/{filename}"
        with open(path.joinpath(filename), "wb") as handle:
            handle.write(pkg_resources.resource_string("registers", cf_path))

    manifest = yaml.load(pkg_resources.resource_stream("registers", "data/cloudfoundry/manifest.yml"), Loader=yaml.BaseLoader)  # type: ignore #TODO review type warning # NOQA
    manifest["applications"][0]["name"] = register.uid # NOQA

    with open(path.joinpath("manifest.yml"), "w") as handle: # type: ignore #TODO review type warning # NOQA
        handle.write(yaml.dump(manifest))


def _attr_schema(attribute) -> Union[str, Dict]:
    if attribute.cardinality == Cardinality.One:
        return {"type": "string"}

    return {"type": "array", "items": {"type": "string"}}


def write_resource(path: Path, obj, headers):
    """
    Generates the pair of files (csv, json) for the given object.
    """

    utils.write_csv_resource(path, obj, headers)
    utils.write_json_resource(path, obj)
