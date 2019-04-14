# -*- coding: utf-8 -*-

"""
This module implements the build command.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

import json
import shutil
from zipfile import ZipFile
from pathlib import Path
from typing import List, Union, Dict
import pkg_resources
import yaml
import click
from .. import rsf, log, Register, Entry, Record, Cardinality
from ..exceptions import RegistersException
from . import utils
from .utils import error


@click.command(name="build")
@click.argument("rsf_file", type=click.Path(exists=True))
@click.option("--target", type=click.Choice(["netlify",
                                             "cloudfoundry",
                                             "docker"]),
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

        with utils.progressbar(range(1, len(cmds)),
                               label="Loading register") as bar:
            register = Register(cmds, lambda: bar.update(1))

        utils.check_readiness(register)

        build_path = Path(f"build/{register.uid}")

        if build_path.exists():
            shutil.rmtree(build_path)

        build_path.mkdir(parents=True)

        if target == "netlify":
            build_target_resource("_redirects", "netlify", build_path)

        if target == "docker":
            build_docker(build_path)

        if target == "cloudfoundry":
            build_cloudfoundry(build_path, register)

        if target in ["cloudfoundry", "docker"]:
            build_path = build_path.joinpath("public")
            build_path.mkdir()

        build_blobs(build_path.joinpath("items"), register)
        build_entries(build_path.joinpath("entries"), register)
        build_records(build_path.joinpath("records"), register)
        build_commands(build_path.joinpath("commands"), register)
        build_context(build_path.joinpath("register"), register)
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
    """
    Creates files for the cloudfoundry target.
    """

    build_target_resource("buildpack.yml", "cloudfoundry", path)
    build_target_resource("mime.types", "nginx", path)
    build_target_resource("nginx.conf", "nginx", path)
    build_lua_resources(path)

    with open(path.joinpath("default.conf"), "w") as handle:
        filename = "data/nginx/default.conf"
        conf = pkg_resources.resource_string("registers", filename)
        res = conf.decode("utf-8").replace("listen 80", "listen {{port}}")
        handle.write(res)

    with open(path.joinpath("manifest.yml"), "w") as handle:
        filename = "data/cloudfoundry/manifest.yml"
        stream = pkg_resources.resource_stream("registers", filename)
        manifest = yaml.load(stream, Loader=yaml.BaseLoader)  # type: ignore
        manifest["applications"][0]["name"] = register.uid

        handle.write(yaml.dump(manifest))


def build_docker(path: Path):
    """
    Creates files for the docker target.
    """

    build_target_resource("default.conf", "nginx", path)
    build_target_resource("Dockerfile", "docker", path)
    build_target_resource("docker-compose.yml", "docker", path)
    build_target_resource("mime.types", "nginx", path)

    build_lua_resources(path)


def build_lua_resources(path: Path):
    """
    Creates files for nginx lua files.
    """

    path.joinpath("lua").mkdir()

    build_target_resource("lua/registers.lua", "nginx", path)
    build_target_resource("lua/utils.lua", "nginx", path)
    build_target_resource("lua/errors.lua", "nginx", path)


def build_target_resource(name: str, target: str, path: Path):
    """
    Creates a file for the given target.
    """

    with open(path.joinpath(name), "wb") as handle:
        resource = pkg_resources.resource_string("registers",
                                                 f"data/{target}/{name}")
        handle.write(resource)


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
