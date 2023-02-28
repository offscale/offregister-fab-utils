#!/usr/bin/env python

__author__ = "Samuel Marks"
__version__ = "0.0.31"

from collections import namedtuple

skip_apt_update = False
skip_yum_update = False
skip_dnf_update = False

Package = namedtuple("Package", ("name", "version"))

__all__ = ["skip_apt_update", "skip_dnf_update", "skip_yum_update", "Package"]
