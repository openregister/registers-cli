import json
import csv
from .. import rsf, xsv, Register, Blob, validator
from . import utils


def validate(blob, rsf_path):
    cmds = rsf.read(rsf_path)
    r = Register(cmds)

    utils.check_readiness(r)

    schema = r.schema()

    data = json.loads(blob)
    validator.validate(data, schema)

    return {"blob": Blob(data), "register": r}


def ls(rsf_path, output_format=None, stream=None):
    cmds = rsf.read(rsf_path)
    r = Register(cmds)

    utils.check_readiness(r)
    blobs = r.log.blobs

    if output_format == "csv":
        schema = r.schema()
        headers = [attr.uid for attr in schema.attributes]
        writer = csv.writer(stream)
        writer.writerow(headers)

        for blob in blobs.values():
            row = xsv.serialise_object(blob, headers=headers)
            writer.writerow(row)

        stream.seek(0)

        return writer

    if output_format == "json":
        json.dump({repr(k): v for k, v in blobs.items()}, stream,
                  ensure_ascii=False, indent=2, cls=utils.JsonEncoder)

        stream.seek(0)

        return None

    return blobs.values()
