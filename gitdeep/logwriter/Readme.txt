========
logwriter
========

1. 概要
  * ログの記録を行う。
  * デバッグ用関数アノテーションを行う。

2. 必要なシステム
  * six
    > python -m pip install six --user --upgrade

3. 機能
  * ログの記録
    * logging.Loggerを継承する。
    * confファイルから入力されたログ設定の型の変換を行う(str->int)。
    * debugメッセージにてファイル名と行番号を付加する。

  * デバッグ用関数アノテーションを行う。
    * @logwriter.debug
    * @logwriter.elapsed
    * @logwriter.obsolete

4. ビルド方法
  それぞれのディレクトリでsetupを実行する。
  $ python3.4 setup.py bdist_wheel --universal
