# -*- coding: utf-8 -*-

"""
Register Serialisation Format (RSF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Register Serialisation Format (RSF) is currently unspecified. The work in
progress can be found here:

<https://github.com/openregister/registers-rfcs/blob/3c97dd876974a3cf85a2f5717e398a270afd3a8f/content/rsf-spec/index.md>

:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""


from typing import List
from .core import (Action, Command, # NOQA
                   add_item, assert_root_hash, append_entry)
from .parser import parse, load # NOQA


def read(filepath: str) -> List[Command]:
    """
    Reads an RSF file::

        from registers import rsf
        commands = rsf.read('country.rsf')
    """

    with open(filepath, 'r') as handle:
        return parse(handle)


def dump(commands: List[Command]) -> str:
    """
    Stringifies the given list of commands.
    """

    return "\n".join([str(command) for command in commands]) + "\n"
