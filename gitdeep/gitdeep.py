#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下位ディレクトリを含めてgitを実行します。
"""

__author__ = "Kazuyuki OHMI"
__version__ = "1.0.0"
__date__    = "2016/05/09"
__license__ = 'MIT'

import logging
import os.path
import re
import sys
import subprocess


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

    # 変数を初期化する。
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

        line = "cd '{dir}' && git {cmd} {args}".format(
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
    :param str dir_match:   マッチング正規化表現式(ディレクトリ名に対して行う)
    :rtype:                 list
    :return:                ファイルのリスト
    """

    # 変数を初期化する。
    results = []
    if path_search.endswith(os.sep):
        path_search = path_search.rstrip(os.sep)

    for root, dirs, _files in os.walk(path_search):

        # ディレクトリ毎の処理を行う。
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

    # 変数を初期化する。
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

    # 変数を初期化する。
    symbol_type = SYMBOLS[symbol_type]
    base = {}

    for digit, unit in enumerate(symbol_type[1:]):
        base[unit] = 1 << (digit+1)*10

    for symbol in reversed(symbol_type[1:]):
        if byte >= base[symbol]:
            value = float(byte) / base[symbol]
            return fmt % dict(value=value, symbol=symbol)

    return fmt % dict(symbol=symbol_type[0], value=byte)


def console_main():
    """
    console_scripts entry point
    """

    print(call(*sys.argv[1:], verbose=True))

    return 0


if __name__ == "__main__":
    """
    self entry point
    """
    sys.exit(console_main())
