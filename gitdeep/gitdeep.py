#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下位ディレクトリを含めてgitを実行します。
"""

# Compatible module
from __future__ import absolute_import
from __future__ import unicode_literals

# Buitin module
import argparse
import logging
import os
import re
import sys
import subprocess

# Local module
if "." in __name__:
    from . import logwriter
    from . import cmdparser
else:
    import logwriter
    import cmdparser

# Global variable
__author__ = "Kazuyuki OHMI"
__version__ = "1.0.8"
__date__    = "2016/12/12"
__license__ = 'MIT'

def call(cmd, args, **kwargs):
    """
    下位ディレクトリを含めて、コマンドを実行する。
    :param str cmd:      コマンド
    :param list args:    引数
    :param bool verbose: コンソールで実行時にメッセージを表示する。
    :param bool debug:   デバッグオプション
    :rtype:              int
    :return:             0:正常終了
    """

    # 変数を初期化します。
    ret = 0
    verbose = kwargs.get("verbose")
    _debug = kwargs.get("debug")

    # 下位ディレクトリを取得する。
    dnames = get_dirs(".", "^.git$")
    paths = map(lambda dname: os.path.realpath(dname), dnames)
    for path in paths:
        path_base = os.path.realpath(os.path.join(path, ".."))
        dname = os.path.basename(path_base)

        if verbose:
            print("----- %s -----" % dname)
            print("path: %s" % path_base)
            print("size: %s" % bytes2str(du(path_base)))
            print("")

        line = 'cd "{dir}" && git {cmd} {args}'.format(
                    dir=path_base, cmd=cmd, args=" ".join(args))
        ret, _txt = popen(line, echo=True, abort=True)
        print("")

        if ret !=0:
            sys.exit(ret)

    return ret

def get_dirs(path_search="", dir_match=".*"):
    """
    パス以下のファイルを取得する。
        名前順にソートする。
    :param str path_search: パス名
    :param str dir_match:   マッチング正規化表現式(ディレクトリ名に対して行います)
    :rtype:                 list
    :return:                ファイルのリスト
    """

    # 変数を初期化します。
    results = []
    if path_search.endswith(os.sep):
        path_search = path_search.rstrip(os.sep)

    for root, dirs, _files in os.walk(path_search):

        # ディレクトリ毎の処理を行います。
        for dname in dirs:
            match = re.search(dir_match, dname)
            if match != None:
                results.append(os.path.join(root, dname))

    # ソートする。
    results.sort()

    return results

def popen(cmd, echo=True, abort=False):
    """
    コマンドを実行する。
    :param unicode cmd:     コマンド
    :param bool echo:       コマンドを表示する。戻り値の出力文字列はNoneになる。
    :param bool abort:      戻り値が0でない場合終了する。
    :rtype:                 tuple
    :return:                戻り値、出力文字列
    """

    if echo:
        sys.stdout.write("$ %s%s"  % (cmd, os.linesep))

    if echo:
        ps = subprocess.Popen(cmd, shell=True, stdout=sys.stdout)
    else:
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    _ps_pid = ps.pid

    stdout_data, stderr_data = ps.communicate()

    # パイプを閉じる。
    if echo:
        pass
    else:
        ps.stdout.close()

    ret = ps.wait()

    if stdout_data:
        txt = stdout_data.decode('utf-8')
    else:
        txt = None

    if abort and ret!=0:
        sys.exit("コマンドの実行に失敗しました。\n\t%s\n\t%d\n\t%s" % (cmd, ret, stderr_data))

    return (ret, txt)

def du(path, *args, **kwargs):
    """
    pathに含まれるファイルのバイト数を取得する。
    :param str path: パス
    :rtype:          int
    :return:
    """

    # 変数を初期化します。
    _debug = kwargs.get("debug")
    logger = kwargs.get("logger")
    if not logger:
        logger = logging.getLogger(__file__)

    byte = 0

    for root, _dirs, files in os.walk(path):

        for fname in files:
            path = os.path.join(root, fname)
            if os.path.isfile(path):
                byte += os.path.getsize(path)

    return byte

def bytes2str(byte, fmt='%(value).0f %(symbol)sB', symbol_type='short'):
    """
    バイト数をテキストにする。
    :param int byte: バイト数
    :rtype:          str
    :return:         バイト数を表すテキスト
    """

    SYMBOLS = {
        'short'     : ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
        'long' : ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
                           'zetta', 'iotta'),
    }

    # 変数を初期化します。
    symbol_type = SYMBOLS[symbol_type]
    base = {}

    for digit, unit in enumerate(symbol_type[1:]):
        base[unit] = 1 << (digit+1)*10

    for symbol in reversed(symbol_type[1:]):
        if byte >= base[symbol]:
            value = float(byte) / base[symbol]
            return fmt % dict(value=value, symbol=symbol)

    return fmt % dict(symbol=symbol_type[0], value=byte)

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

def main():
    """
    console_scripts entry point
    """

    # 変数を初期化します。
    result = 0
    logger = logwriter.LogWriter("gitdeep")

    # 引数の処理を行います。
    parser = argparse.ArgumentParser(
                     description=__doc__.strip(os.linesep))
    values = parse_docstring(call)
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
            result = call(verbose=True, **vars(args))

        except KeyboardInterrupt as ex:
            sys.stderr.write(u"中断しました。")
            sys.stderr.write(os.linesep)

    return result

if __name__ == "__main__":
    """
    self entry point
    """
    sys.exit(main())
