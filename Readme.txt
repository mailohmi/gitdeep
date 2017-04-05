============
gitdeep
============

1. 概要
  * 下位ディレクトリを含めてgitを実行します。

  注) 下位ディレクトリをまとめて処理されるため、更新を伴う操作(git commit 等)は、個別に行って下さい。

2. 必要なシステム
  * git
  * python
  * python six

3. セットアップ方法
  (1) インストール
    * pipからインストールする場合
    	以下のコマンドにより直接インストールできます。
    	$ python -m pip install --user --upgrade git+https://github.com/mailohmi/gitdeep.git

    	インストールすると、以下のコマンドによりパッケージが表示されます。
    	$ python -m pip list
    	gitdeep (*.*.*)

  (2) ソースコードを取得する場合
    以下のコマンドより取得します。
    Github
      $ git clone https://github.com/mailohmi/gitdeep.git
    
    インストールします。
      $ cd gitdeep
      $ python -m pip install --upgrade .

  (3) PATHの設定
    インストール後に、環境変数のPATHを設定します。
    以下のコマンドを実行するとパスが表示されるので、そのパスをPATHに設定します。
    $ python -c 'import os;import site; print(os.path.join(site.getuserbase(), "bin"))'

    ex)
      > @powershell -NoProfile -ExecutionPolicy Bypass -Command "$path = [Environment]::GetEnvironmentVariable('PATH', 'User');$path += ';%USERPROFILE%\AppData\Roaming\Python\Python35\Scripts';[Environment]::SetEnvironmentVariable('PATH', $path, 'User')"

  (4) 動作確認
    以下のコマンドにより、ヘルプが表示されれば、問題ありません。
  	$ gitdeep -h
  	usage: gitdeep [-h] [--debug] cmd [args [args ...]]

  	下位ディレクトリを含めてgitを実行します。

  	positional arguments:
  	  cmd         コマンド
  	  args        引数
  	...

  (5) アンインストール
    * 以下のコマンドを実行します。
      $ python -m pip uninstall gitdeep

  (6) zip アーカイブ
    以下のコマンドより実行アーカイブにします (> python3.5)。
    > python -m zipapp gitdeep --python python

4. 使用方法
  * コマンドから実行する(gitdeep)。
    下位ディレクトリを含めて、"git status" を実行します。
    $ gitdeep status

5. 履歴
  1.0 git_subdirより移行しました。
