from typing import Dict, Any
from .. import rsf, xsv, Register, Patch
from . import utils


def create(xsv_file, rsf_file, timestamp, apply_flag=False):
    """
    Creates an RSF patch.
    """

    cmds = rsf.read(rsf_file)
    r = Register(cmds)

    utils.check_readiness(r)

    schema = r.schema()

    with open(xsv_file, "r", newline="") as handle:
        blobs = xsv.deserialise(handle, schema)
        patch = Patch(schema, blobs, timestamp)

        if apply_flag:
            r.apply(patch)

            return _apply(patch, rsf_file)

        return patch.commands


def apply(patch_file, rsf_file):
    """
    Applies an RSF patch.
    """

    cmds = rsf.read(rsf_file)
    r = Register(cmds)

    utils.check_readiness(r)

    schema = r.schema()

    patch_cmds = rsf.read(patch_file)
    patch = Patch(schema, patch_cmds)
    r.apply(patch)

    return _apply(patch, rsf_file)


def _apply(patch: Patch, rsf_file: str) -> Dict[str, Any]:
    """
    Applies a patch and saves RSF to the given file.
    """

    with open(rsf_file, "a") as handle:
        handle.writelines([f"{cmd}\n" for cmd in patch.commands])

    summary = {
        "added_commands_number": len(patch.commands)
    }

    return summary
