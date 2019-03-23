import json
import click
from .. import Register, Blob, Entry, Record, Hash
from ..exceptions import CommandError


def error(message):
    """
    Sends a message to stderr and exits with code error 1.
    """

    click.secho(message, fg="red", bold=True, err=True)
    exit(1)


def note(message):
    """
    Sends a message to stdout.
    """

    click.secho(message, fg="yellow", bold=True)


def ok(message):
    """
    Sends a message to stdout.
    """

    click.secho(message, fg="green", bold=True)


def check_readiness(register: Register):
    if not register.is_ready():
        msg = "The given RSF does not have enough information to be used in this command." # NOQA
        raise CommandError(msg)


def serialise_json(obj, stream):
    json.dump(obj, stream, ensure_ascii=False, indent=2, cls=JsonEncoder)


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


def progressbar(iterable, **kwargs):
    tpl = click.style("[%(bar)s] %(info)s %(label)s", fg="bright_yellow")
    bar = click.progressbar(iterable,
                            show_eta=False,
                            show_percent=True,
                            bar_template=tpl,
                            **kwargs)

    bar.short_limit = 0.1

    return bar
