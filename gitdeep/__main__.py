#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
パッケージエントリ
"""

__author__ = "Kazuyuki OHMI"
__version__ = "1.0.2"
__date__    = "2016/05/09"
__license__ = 'MIT'

import argparse
import os
import re
import sys
import gitdeep

def parse_docstring(func):
    """
    Sphinx スタイルの docstrings をパースする。
        関数の説明は、"description"で取得する。
        変数の説明は、変数名で取得する。

    :param function func: 関数
    """

    values = {}
    text = func.__doc__

    # name
    values["name"] = func.__name__

    # description を設定する。
    m_desc = re.search(r"([\s\S]*?):", text)
    if m_desc:
        values["description"] = m_desc.group(1).strip()
    else:
        values["description"] = ""

    fileds = re.findall(r"(\S*:.*?:.*)", text)

    # パラメータを設定する。
    for filed_line in fileds:
        match = re.search(r":param\s*(.*)\s(.+):(.*)", filed_line)
        if match:
            typ = None
            txt_type = match.group(1).strip()
            txt_name = match.group(2).strip()
            txt_help = match.group(3).strip()

            if txt_type == "int":
                typ = int
            elif txt_type == "str":
                typ = str
            elif txt_type == "list":
                typ = list
            elif txt_type == "tuple":
                typ = tuple
            elif txt_type == "bytes":
                typ = bytes
            elif txt_type == "bool":
                typ = bool

            values[txt_name] = {"help": txt_help, "type":typ}

    return values


def console_main():
    """
    console_scripts entry point
    """
    # 変数を初期化する。
    cwd = os.getcwd()
    result = 0

    # 引数の処理を行う。
    parser = argparse.ArgumentParser(
                     description=gitdeep.__doc__.strip(os.linesep))
    values = parse_docstring(gitdeep.call)
    values["debug"].pop("type")
    parser.add_argument(
        '--debug', action='store_true', default=False, **values["debug"])
    parser.add_argument(
        '--version', action='version', version=__version__)
    parser.add_argument('cmd', **values["cmd"])
    values["args"]["type"] = str
    parser.add_argument('args', nargs="*", **values["args"])

    # コマンドを処理する。
    args = parser.parse_args()
    if not hasattr(args, 'cmd'):
        parser.error(u'引数が不足しています。')
        sys.exit(-1)
    else:
        try:
            result = gitdeep.call(verbose=True, **vars(args))

        except KeyboardInterrupt as ex:
            sys.stderr.write(u"中断しました。")
            sys.stderr.write(os.linesep)

    # カレントディレクトリを復帰する。
    os.chdir(cwd)
    return result


if __name__ == "__main__":
    """
    self entry point
    """
    sys.exit(console_main())
