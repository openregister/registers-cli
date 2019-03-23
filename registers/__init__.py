# -*- coding: utf-8 -*-
# flake8: NOQA

"""
Registers
~~~~~~~~~

Registers is a Python library to back up a command line inteface (CLI). It
relies on the Register Serialisation Format (RSF) as the source of data to
construct the register state in memory. At the moment there are no plans to
provide any non-memory backend.

This library implements the Registers data model defined by the `Registers
Specification Version 1 <https://spec.openregister.org/v1/>`_.

Basic usage:

   >>> from registers import rsf, Register
   >>> commands = rsf.read("tests/fixtures/country.rsf")
   >>> r = Register(commands)
   >>> r.stats()
   {'data': {'total-entries': 209, 'total-blobs': 209}, \
'metadata': {'total-entries': 18, 'total-blobs': 16}}

   Get the current state of the data held in the register:

   >>> records = r.records()
   >>> records.get("GB").get("name")
   'United Kingdom'


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from .blob import Blob, Value
from .entry import Entry, Scope
from .hash import Hash
from .log import Log
from .record import Record
from .register import Register
from .schema import Schema, Attribute, attribute, Datatype, Cardinality
from .patch import Patch
