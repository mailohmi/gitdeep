============
gitdeep
============

1. 概要
  * 下位ディレクトリを含めてgitを実行します。

  * 注) 下位ディレクトリをまとめて処理されるため、更新を伴う操作(git commit 等)は、個別に行つて下さい。

2. 必要なシステム
  * python3.4
  * git

3. セットアップ方法
  URL: https://github.com/mailohmi/gitdeep/

  (1) インストール
    * pipからインストールする場合
    	以下のコマンドにより直接インストールできます。
    	$ python3.4 -m pip install --user git+https://github.com/mailohmi/gitdeep.git

    	インストールすると、以下のコマンドによりパッケージが表示されます。
    	$ python3.4 -m pip list
    	git-subdir (0.0.0)

    * ソースコードを取得する場合
      Github
      $ git clone https://github.com/mailohmi/gitdeep.git

  (2) PATHの設定
    インストール後に、環境変数のPATHを設定します。
    以下のコマンドを実行するとパスが表示されるので、そのパスをPATHに設定します。
    $ python3.4 -c 'import os;import site; print(os.path.join(site.getuserbase(), "bin"))'
    -> .../Python/3.4/bin

    以下のコマンドにより、ヘルプが表示されれば、問題ありません。
  	$ gitdeep -h
  	usage: gitdeep [-h] [--debug] cmd [args [args ...]]

  	下位ディレクトリを含めてgitを実行します。

  	positional arguments:
  	  cmd         コマンド
  	  args        引数
  	...

  (3) アンインストール
    * 以下のコマンドを実行します。
      $ python3.4 -m pip uninstall git-subdir

4. 使用方法
  * コマンドから実行する(gitdeep)。
    下位ディレクトリを含めて、"git status" を実行します。
    $ gitdeep status

5. 履歴
  1.0 git_subdirより移行した。
