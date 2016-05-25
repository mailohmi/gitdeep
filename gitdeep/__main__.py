#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
パッケージエントリ
"""

# Compatible module
from __future__ import absolute_import
from __future__ import unicode_literals

# Buitin module
import os
import sys

# Local module
sys.path.append(os.path.join(os.path.dirname(__file__)))
import gitdeep

# Global variable
__author__ = "Kazuyuki OHMI"
__version__ = "1.0.4"
__date__    = "2016/05/16"
__license__ = 'MIT'

if __name__ == "__main__":
    """
    self entry point
    """
    sys.exit(gitdeep.main())
