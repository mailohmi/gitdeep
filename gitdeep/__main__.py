#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
パッケージエントリ
"""

# 互換モジュール
from __future__ import absolute_import
from __future__ import unicode_literals

# システムモジュール
import os
import sys

# ローカルモジュール
sys.path.append(os.path.join(os.path.dirname(__file__)))
import gitdeep

# グローバル変数
__author__ = "Kazuyuki OHMI"
__version__ = "1.0.3"
__date__    = "2016/05/16"
__license__ = 'MIT'

if __name__ == "__main__":
    """
    self entry point
    """
    sys.exit(gitdeep.main())
