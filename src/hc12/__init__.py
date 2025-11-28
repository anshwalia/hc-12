#!/usr/bin/env python
#
# This module provides support for accessing and configuring HC-12 serial wireless module
#
# This file is part of HC-12 library. https://github.com/anshwalia/hc-12
# (C) 2025 Ansh Walia <anshwalia@outlook.com>

__all__ = ["HC12", "HC12Settings"]

from .data_models import HC12Settings
from .wrapper import HC12
