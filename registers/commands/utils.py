import json
from .. import Register, Blob, Entry, Record, Hash
from ..exceptions import CommandError


def check_readiness(register: Register):
    if not register.is_ready():
        msg = "The given RSF does not have enough information to be used in this command." # NOQA
        raise CommandError(msg)


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Hash):
            return repr(obj)

        if isinstance(obj, Blob):
            return obj.to_dict()

        if isinstance(obj, Entry):
            return obj.to_dict()

        if isinstance(obj, Record):
            return obj.to_dict()

        return json.JSONEncoder.default(self, obj)
