#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ログの記録を行います。
"""

# Compatible module
from __future__ import absolute_import
from __future__ import unicode_literals
import six

# Buitin module
import datetime
import functools
import inspect
import logging.handlers
import os
import stat
import sys
import time
import unittest

# Global variable
__author__ = "Kazuyuki OHMI"
__version__ = "3.3.4"
__date__    = "2016/05/22"
__license__ = "MIT"

RAISE_NameError = True      # getLogger()にて LogWriter を見つけられない場合に例外を送信します。
_ENABLE_PROFILE = None      # profile_begin() から有効にします。
_PROFILE_MAX = 100          # 最大の関数集計数
_PROFILE_COUNT = 0          # 関数集計数
_PROFILES = []              # 関数集計の配列です。
_LOGGERS = []               # ロガーオブジェクト配列
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

class LogWriter(logging.Logger):
    """
    ロガー
    * confファイルから読み込んだ型を修正します。
    * debug()関数に行番号を追加します。
    * levelでは以下の値を使用します。
        CRITICAL    50
        ERROR       40
        WARNING     30
        INFO        20
        DEBUG       10
        NOTSET      0
    * ディレクトリセパレータを変換します。
    """

    formats = ["%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        "%(asctime)s %(message)s",                               
        "%(message)s",]

    conf = {
        "level": logging.INFO,      # Set the root logger level to the specified level.
        "format": formats[2],       # Use the specified format string for the handler (Default).
        "format_stdout": formats[3],# Use the specified format string for stdout handler.
        "stdout": True,             # Add stdout handler.
        "filename": None,           # Add add RotatingFileHandler.
        "maxBytes": 1024 * 1024,    # max bytes of log file.
        "backupCount": 2,           # backup count of log file.
        }

    @property
    def version(self):
        return __version__

    class Filter(logging.Filter):
        """
        ログフィルタ
        """

        level = None

        def __init__(self, level=logging.WARNING):
            self.level = level

        def filter(self, record):
            return record.levelno >= self.level

    class TimeFormatter(logging.Formatter):
        converter = datetime.datetime.fromtimestamp

        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)

            if datefmt:
                s = ct.strftime(datefmt)
            else:
                t = ct.strftime("%Y/%m/%d %H:%M:%S")
                s = "%s,%03d" % (t, record.msecs)
            return s

    def __init__(self, name="root", level=logging.INFO, **kwargs):
        """
        コンストラクタ

        :param str name:        ログ名称
        :param str level:       ログレベル
        :param bool stdout:     標準出力に出力する。
        """

        # 変数を初期化します。
        global _LOGGERS

        self.conf.update({"name": name})
        self.conf.update({"level": level})
        self.conf.update(**kwargs)

        # confファイルから読み込んだ型を修正します。
        if not isinstance(self.conf.get("level"), int):
            self.conf["level"] = int(self.conf["level"])

        if not isinstance(self.conf.get("stdout"), bool):
            self.conf["stdout"] = bool(self.conf["stdout"])

        filename = self.conf["filename"]
        if filename is not None:
            self.conf["filename"] = self.conf.get("filename").replace("/", os.path.sep)

            prefix = self.conf.get("prefix")
            if prefix is not None:
                self.conf["filename"] = os.path.join(prefix, self.conf["filename"])

        if not isinstance(self.conf.get("maxBytes"), int):
            self.conf["maxBytes"] = int(self.conf["maxBytes"])

        if not isinstance(self.conf.get("backupCount"), int):
            self.conf["backupCount"] = int(self.conf["backupCount"])

        # ベースクラスのコンストラクタを呼び出します。
        logging.Logger.__init__(self, self.conf["name"], level=self.conf["level"])

        # 標準出力のハンドラを登録します。
        if self.conf["stdout"]:
            self.add_stdout_handler()

        # ファイルハンドラを登録します。
        if self.conf["filename"]:
            filename = self.conf["filename"]
            maxBytes = self.conf["maxBytes"]
            backupCount = self.conf["backupCount"]

            self.add_file_handler(filename,maxBytes,backupCount)

        # ロガーオブジェクト配列に登録します。
        _LOGGERS.append(self)

    def __str__(self):
        return str(__dict__)

    def __repr__(self):
        values = self.__dict__
        values["conf"] = self.conf
        return str(values)

    def add_stdout_handler(self, dest=sys.stdout):
        """
        標準出力のハンドラを登録します。
        :param file dest:   ログの出力先のストリーム
        :rtype:             None
        """
        fmt = self.conf.get("format_stdout",self.conf.get("format"))

        stdout_handler = logging.StreamHandler(dest)
        stdout_handler.setLevel(self.level)
        stdout_handler.addFilter(self.Filter(self.conf["level"]))
        stdout_handler.setFormatter(self.TimeFormatter(fmt))
        self.addHandler(stdout_handler)

        return

    def add_syslog_handler(self, dest=None):
        """
        ログを転送する。
        :param str/tupple dest: 転送先のホスト
            /dev/log:           Linux
            /var/run/log:       Darwin
        :rtype:                 None
        """

        # 送信先を設定する。
        if not dest:
            path_list = ["/dev/log", "/var/run/syslog"]
            for path in path_list:
                mode = os.stat(path).st_mode
                if stat.S_ISSOCK(mode):
                    dest = path
                    break

            if not dest:
                dest = ("localhost", logging.handlers.SYSLOG_UDP_PORT)

        handler = logging.handlers.SysLogHandler(dest, logging.handlers.SysLogHandler.LOG_USER)

        handler.setFormatter(self.TimeFormatter(self.conf["format"]))
        handler.setLevel(self.conf["level"])
        handler.addFilter(self.Filter(self.conf["level"]))
        self.addHandler(handler)

    def add_file_handler(self, filename, maxBytes=0, backupCount=0):
        """
        ファイルに出力します。
        :param str filename:   出力ファイル名
        :rtype:                None
        """

        # 変数を初期化します。
        if sys.version_info >= (3, 0):
            encoding = sys.getdefaultencoding()
        else:
            encoding = None
        handler = logging.handlers.RotatingFileHandler(filename, maxBytes=maxBytes, backupCount=backupCount,
                encoding=encoding)

        handler.setLevel(self.level)
        handler.addFilter(self.Filter(self.conf["level"]))
        handler.setFormatter(self.TimeFormatter(self.conf["format"]))

        if handler:
            self.addHandler(handler)

    def debug(self, message=u"", frame=None):
        """
        行番号付きでデバッグログを出力します。

        :param u message:       出力するテキスト
        :param Traceback frame: 呼び出し元のフレーム
        :rtype:                 None
        """

        if not self.isEnabledFor(logging.DEBUG):
            return

        # 変数を初期化します。
        msg = message
        if frame is None or not isinstance(frame, inspect.Traceback):
            frame = stack_frame(2)

        if frame is not None:
            path = frame.filename
            file_base, _file_ext = os.path.splitext(os.path.basename(path))
            msg = "%s (%05d) %s" % (file_base, frame.lineno, msg)

        # logging 出力を行う。
        return logging.Logger.debug(self, msg)

    def debug_anchor_begin(self, *args, **kwargs):
        """
        開始ログを出力します。
        関数は、 _func_name で指定します。
        フレームは、 _frame で指定します。

        :rtype:               None
        """

        if not self.isEnabledFor(logging.DEBUG):
            return

        # 変数を初期化します。
        args_txt = get_args_txt(*args, **kwargs)
        frame = kwargs.get("_frame")
        if frame is None:
            frame = stack_frame(2)

        # メッセージを設定します。
        func_name = kwargs.get("_func_name", frame.function)
        msg = "anchor begin: %s(%s)" % (func_name, args_txt)

        # 行番号付きでデバッグログを出力します。
        return self.debug(msg, frame=frame)

    def debug_anchor_end(self, result=None, *args, **kwargs):
        """
        終了ログを出力します。
        関数は、 _func_name で指定します。
        フレームは、 _frame で指定します。
        経過時間は、 _time_elapsed で指定します。

        :param object result:   戻り値
        :rtype:                 None
        """

        if not self.isEnabledFor(logging.DEBUG):
            return

        # 変数を初期化します。
        frame = kwargs.get("_frame")
        if frame is None:
            frame = stack_frame(2)

        argments = get_args_txt(*args, **kwargs)

        values = {u"result":result}

        time_elapsed = kwargs.get(u"_time_elapsed")
        if time_elapsed is not None:
            if isinstance(time_elapsed, (str, float)):
                time_hour, time_rest = divmod(time_elapsed, 3600)
                time_min, time_sec = divmod(time_rest, 60)
                time_elapsed = u"{:0>2}:{:0>2}:{:06.3f}".format(int(time_hour),int(time_min),time_sec)

            values[u"time_elapsed"] = time_elapsed

        # メッセージを設定します。
        func_name = kwargs.get("_func_name", frame.function)
        values_txt = get_args_txt(**values)
        msg = u"anchor end: %s(%s) %s" % (func_name, argments, values_txt)

        # 行番号付きでデバッグログを出力します。
        return self.debug(msg, frame=frame)

def get_args_txt(*args, **kwargs):
    """
    引数をテキストにします。
    変数名が "_" で始まる変数はスキップします。

    :rtype:         str
    :return:        変換したテキスト
    """

    # 変数を初期化します。
    args_txt = u""

    # argsを展開します。
    for value in args:
        if args_txt != u"":
            args_txt += u", "
        args_txt += repr(value)

    # kwargsを展開します。
    for key, value in kwargs.items():

        # 変数名が "_" で始まる変数はスキップします。
        if key.startswith("_"):
            continue

        if args_txt != u"":
            args_txt += u", "
        args_txt += u"%s=%s" % (ascii_repr(key), repr(value))

    return args_txt

def ascii_repr(txt):
    """
    アスキー変換を行います。

    :param u txt:   テキスト
    :rtype:         str
    :return:        変換したテキスト
    """

    # 変数を初期化します。
    raw = b""

    while True:
        if isinstance(txt, int):
            raw = str(txt)
            break

        # リテラル形式に変換する。
        raw = repr(txt)

        # unicode表記を除外する。
        if raw.startswith(u"u'") and raw.endswith(u"'"):
            raw = raw[2:-1]

        # シングルクオートを除外する。
        if raw.startswith(u"'") and raw.endswith(u"'"):
            raw = raw.strip(u"'")

        break

    return raw

def getLogger(name=None, *args, **kwargs):
    """
    LogWriter を取得します。
    名前を指定しない場合、name=Noneを設定します。

    :param u name:      ロガーの名前
    :rtype:             LogWriter
    :return:            ロガー
    .. note::           引数からLogWriterを検索します。
    .. note::           ロガーオブジェクト配列から最後に初期化したLogWriterを検索します。
    """

    # 変数を初期化します。
    logger = None

    while True:
        # args から Logger を取得します。
        for arg in args:
            if isinstance(arg, LogWriter):
                logger = arg
                break

        # kwargs から Logger を取得します。
        for _key, value in kwargs.items():
            if isinstance(value, LogWriter):
                logger = value
                return logger

        # フレームを取得します。
        stacks = inspect.stack()
        for stackindex in range(len(stacks) - 1, -1, -1):

            stack = stacks[stackindex]
            frame = stack[0]
            filename = stack[1]

            if os.path.splitext(filename)[0] == os.path.splitext(__file__)[0]:

                # ロガーオブジェクト配列を取得します。
                loggers = frame.f_globals.get("_LOGGERS")
                if len(loggers) == 0:
                    break

                if name is None:
                    logger = loggers[-1]
                    return logger
                else:
                    for loggerindex in range(len(loggers) - 1, -1, -1):
                        logger = loggers[loggerindex]
                        if logger.name == name:
                            return logger

        if RAISE_NameError:
            raise NameError(u"LogWriter(%s) was not found." % name)
        else:
            # ロガーを取得します。
            logger = LogWriter(filename)
            break

    return logger

def stack_frame(context=2):
    """
    スタックフレームを取得します。

    :param int stackIndex:      スタック番号
    :rtype:                     Taceback
    :return:                    スタックの内容
    """
    stacks = inspect.stack()
    if context >= len(stacks):
        return None

    callerframerecord = stacks[context]
    framerecord = callerframerecord[0]
    frameinfo = inspect.getframeinfo(framerecord)

    return frameinfo

"""
function decorator
"""
def profile_func(func):
    """
    実行結果を集計します。
    表示する関数に関数デコレータ"@logwriter.profile_func"をつけます。
    * 引数に設定された LogWriter を使用します。
    * 呼び出し元のグローバル変数の LogWriter を使用します。

    :param function func_name:  関数
    :rtype:                     object
    :return:                    関数の戻り値
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        # 変数を初期化します。
        pass

        # 引数をテキストにします。
        argments = get_args_txt(*args, **kwargs)

        # ロガーを取得します。
        logger = getLogger(None, *args, **kwargs)

        if isinstance(logger, LogWriter):

            # 呼び出し元のフレームを取得します。
            frame = stack_frame(2)

            # 開始ログを出力します。
            logger.debug_anchor_begin(_func_name=func.func_name, _frame=frame, *args, **kwargs)

        # 関数を実行します。
        time_start = time.time()
        result = func(*args, **kwargs)
        time_elapsed = time.time() - time_start

        if isinstance(logger, LogWriter):

            # 終了ログを出力します。
            logger.debug_anchor_end(result, _time_elapsed=time_elapsed, _func_name=func.func_name, _frame=frame, *args, **kwargs)

        # 関数を集計対象にします。
        if six.PY2:
            filename = func.func_code.co_filename
            lineno = func.func_code.co_firstlineno
            func_name=func.func_name

        else:
            filename = func.__code__.co_filename
            lineno = func.__code__.co_firstlineno
            func_name=func.__code__.co_name

        if _ENABLE_PROFILE:
            profile_append(filename, lineno,func_name,argments, result, time_elapsed)

        return result

    return wrapper

def profile_begin(*args, **kwargs):
    """
    関数集計を開始します。

    :rtype:                     None
    """

    # 変数を初期化します。
    global _ENABLE_PROFILE
    _ENABLE_PROFILE = True

    # ロガーを取得します。
    logger = getLogger(None, *args, **kwargs)
    logger.info("-" * 8 + " profile begin " + "-" * 8)

    return

def profile_append(file_name, lineno, func_name, argments, result, time_elapsed, *args, **kwargs):
    """
    関数を集計対象にします。

    :param u file_name:         ファイル名
    :param int lineno:          行番号
    :param b func_name:         関数の名前
    :param b argments:          関数の引数
    :param object result:       関数の戻り値
    :param datetime time_elapsed: 経過時間
    :rtype:                     None
    """
    
    # 変数を初期化します。
    global _PROFILES
    global _ENABLE_PROFILE
    global _PROFILE_COUNT

    if not _ENABLE_PROFILE:
        return

    _PROFILE_COUNT += 1
    if _PROFILE_COUNT >= _PROFILE_MAX:
        logger = getLogger(None, *args, **kwargs)
        logger.warn(u"The number profile reach the maximum limit of %d." % _PROFILE_MAX)
        profile_end(*args, **kwargs)
        return
        
    # 行を追加します。
    for profile in _PROFILES:
        profile_file_name = profile.get("file_name")
        profile_lineno = profile.get("lineno")
        profile_func_name = profile.get("func_name")

        if profile_file_name == file_name and profile_lineno == lineno:
            funcs = profile.get("funcs")
            funcs.append({
                    "argments":argments, 
                    "result":repr(result), 
                    "time_elapsed":time_elapsed,
                })

            return

    _PROFILES.append({
            "file_name": file_name, 
            "lineno": lineno, 
            "func_name": func_name, 
            "funcs":[{
                "argments":argments, 
                "result":repr(result), 
                "time_elapsed":time_elapsed,
                }]
            })

    return

def profile_end(*args, **kwargs):
    """
    集計結果を終了します。

    :param function func_name:  関数
    :rtype:                     None
    :return:                    関数の戻り値
    """

    # 変数を初期化します。
    global _ENABLE_PROFILE
    global _PROFILES
    global _PROFILE_COUNT

    # 関数の集計を停止します。
    _ENABLE_PROFILE = False

    # ロガーを取得します。
    logger = getLogger(None, *args, **kwargs)
    logger.info("-" * 8 + " profile end   " + "-" * 8)

    for profile in _PROFILES:
        file_name = os.path.basename(profile.get("file_name"))
        lineno = profile.get("lineno")
        func_name = profile.get("func_name")
        funcs = profile.get("funcs")
        time_elapsed_all = [func.get("time_elapsed") for func in funcs]
        count = len(time_elapsed_all) 

        time_elapsed_ave = sum(time_elapsed_all) / len(time_elapsed_all) 
        time_elapsed_max = max(time_elapsed_all)
        time_elapsed_min = min(time_elapsed_all) 

        msg = "%s, %s: count=%d, ave=%.3fs, max=%.3fs, min=%.3fs" % (file_name,
            func_name,
            count,
            time_elapsed_ave,
            time_elapsed_max,
            time_elapsed_min,)
        logger.info(msg)

    logger.info("-" * 8 + " result  end   " + "-" * 8)

    # 関数集計をクリアします。
    _PROFILES = []
    _PROFILE_COUNT = 0

def obsolete(fname):
    """
    廃止予定の警告を表示する。
    表示する関数に関数デコレータ"@logwriter.obsolete"をつける。

    :param function fname: 関数
    :rtype:                object
    :return:               関数の戻り値
    """

    @functools.wraps(fname)
    def wrapper(*args, **kwds):

        # 変数を初期化します。
        _trace = stack_frame(2)

        sys.stderr.write(
             "%s は廃止予定です。" % (fname.__name__))
        sys.stderr.write(os.linesep)

        # 関数を実行する。
        ret = fname(*args, **kwds)

        return ret

    return wrapper

class TestLogWriter(unittest.TestCase):
    """
    テストケース
    """

    filename = "LogWriter.log"
    logger_conf = {
        "name": os.path.splitext("TestLogWriter"),
        "level": logging.DEBUG,
        }
    logger = None

    def setUp(self):

        # 変数を初期化します。
        self.logger = LogWriter(**self.logger_conf)

    def tearDown(self):
        self.logger = None

    def test_debug(self):
        sys.stdout.write(os.linesep)

        result = self.logger.debug("デバッグ")
        self.assertEqual(result, None)

    def test_debug_anchor_start(self):
        sys.stdout.write(os.linesep)

        # 変数を初期化します。
        arg = "test"

        result = self.logger.debug_anchor_begin(arg=arg)
        self.assertEqual(result, None)

    def test_debug_anchor_end(self):
        sys.stdout.write(os.linesep)

        result = self.logger.debug_anchor_end()
        self.assertEqual(result, None)

@profile_func
def test_dummy1(arg1, arg2, *args, **kwargs):
    return test_dummy2(arg1, arg2) * 2

@profile_func
def test_dummy2(arg1, arg2, *args, **kwargs):
    return arg1 + arg2

class Test(unittest.TestCase):
    """
    テストケース
    """

    logger_conf = {
        "name": os.path.splitext(os.path.basename(__file__))[0],
        "level": logging.DEBUG,
        }

    def setUp(self):

        # 変数を初期化します。
        global logger
        logger = LogWriter(**self.logger_conf)

    def tearDown(self):
        self.logger = None

    def test_get_args_txt(self):
        sys.stdout.write(os.linesep)

        result = get_args_txt(1, 2, test=u"abc")
        self.assertTrue(len(result) > 0)

    def test_profile_func(self):
        sys.stdout.write(os.linesep)

        # 変数を初期化します。
        global _PROFILE_MAX
        global _PROFILES
        global _ENABLE_PROFILE
        global _PROFILE_COUNT

        # 関数集計を開始します。
        profile_begin()     

        result = test_dummy1(1, 2)
        self.assertEqual(result, (1 + 2) * 2)
        test_dummy1(1, 2)

        # 関数集計を終了します。
        result = profile_end()
        self.assertEqual(result, None)

        # クリアします。
        _PROFILES = []
        _PROFILE_MAX = 10
        _PROFILE_COUNT = 0

        profile_begin()
        self.assertEqual(_ENABLE_PROFILE, True)

        for _i in range(0, 11):
            result = test_dummy2(1, 2)

        self.assertEqual(_ENABLE_PROFILE, False)
        self.assertEqual(_PROFILE_COUNT, 0)
        self.assertEqual(_PROFILES, [])

    def test_getLogger(self):
        sys.stdout.write(os.linesep)

        result = getLogger()
        self.assertTrue(isinstance(result, LogWriter))

        result = getLogger(os.path.splitext(os.path.basename(__file__))[0])
        self.assertEqual(result.name, os.path.splitext(os.path.basename(__file__))[0])

def test(*args, **kwargs):
    """
    test entry point
    """
    # 単体テストを実行します。
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLogWriter)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)

    return 0

if __name__ == "__main__":
    """
    self entry point
    """
    sys.exit(test())
