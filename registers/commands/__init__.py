# -*- coding: utf-8 -*-
# flake8: NOQA

"""
This package implements the commands for the Command Line Interface.


:copyright: © 2019 Crown Copyright (Government Digital Service)
:license: MIT, see LICENSE for more details.
"""

from . import patch, blob, utils
from .build import build_command
from .init import init_command
from .context import context_command
from .records import records_command
from .blob import blob_group
from .patch import patch_group
from .value import value_group
