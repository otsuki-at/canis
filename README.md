# Canis
本システムは，計算機上でのユーザのファイル操作をリアルタイムに監視し，監視の結果出力されたファイル操作履歴に対応して操作されたファイルの証跡を保存するシステムである．
また，1日に1回その日に収集された証跡のダイジェストを外部に公開することで，その証跡が公開以降変更されていないことを証明する．

本システムは， [Trigora](https://github.com/nomlab/trigora)を元に作成したシステムである．

# Requirements
+ Python 3.x
+ Redis
+ [libfuse3.14.0](https://github.com/libfuse/libfuse)

# Setup
## Install Redis
### Linux
```
$ sudo add-apt-repository ppa:redislabs/redis
$ sudo apt-get update
$ sudo apt-get install redis
```

# Usage
## Settings
### ログファイルを格納するディレクトリの作成
1. Canis で監視するディレクトリ以外の場所にログファイルを保存するディレクトリを作成する．以下の例では/home 以下に作成したため，ディレクトリの所有者を変更している．
  ```
  $ cd /home
  $ sudo mkdir log
  $ sudo chown $USER log
  $ sudo chgrp $USER log
  ```

### 日次ハッシュ公開先のGitリポジトリ作成
1. 日次ハッシュ公開先として利用する Git リポジトリを作成する．
2. 作成した Git リポジトリをローカルに Clone する．ここでは，daily-hashというリポジトリを例に示す．
  ```
  $ git clone https://github.com/User/daily-hash.git
  ```

### 環境変数の設定
1. 以下の2つのパスについて記述した.envファイルを作成する．
  + DIR には， Canis を保存したディレクトリのパスを定義する．
  + LOGDIR には，ログファイルを格納するために作成したディレクトリのパスを定義する．
  + HASHDIR には，日次ハッシュを公開するGitリポジトリのディレクトリのパスを定義する．
2. `bin/canis` 中の ENVDIR 変数に .env ファイルのパスを設定する．
  ```
  # .envファイルのパスを設定する．
  ENVDIR=/path/of/.env
  ```
3. ファイルに対する操作を fuse-watch.log に記述しないファイルが存在する場合は， .env ファイルに以下のような形式で追加する．2つ以上設定したい場合は， IGNORE1 のようにし，それ以降も IGNORE2, ... のように定義する．
  ```
  IGNORE0=/user.can/path/of/ignore0
  ```

### 日次ハッシュの自動公開設定
1. `bin/upload` 中の ENVDIR 変数に .env ファイルのパスを設定する．
  ```
  ENVDIR=/path/of/.env
  ```
2. `bin/upload` が1日に1回起動するように cron の設定を行う．
  ```
  $ crontab -e
  ```
  cron には以下のように設定を記述する．
  ```
  5 9 * * * /path/of/canis/bin/upload
  ```
  - Canis では時刻をUTCで計測しているため，ユーザごとのタイムゾーンにおけるUTCの0時に相当する時間を設定する．例では，JST における設定を示している
  - 0時(UTC) までの操作がすべてログに記録されてから日次ハッシュをアップロードするために，5分後に upload を起動している

## Launch
以下のように実行するには，`bin/canis` にパスを通す必要がある．
+ システム有効化
  `$ canis start`
+ システム無効化
  `$ canis stop`

## 証跡検索機能
保存している証跡を検索したい場合は，以下のコマンドを利用できる．
  ```
  $ canis info <検索したいファイルのパス>`
  ```

## MCP server
本システムで収集した証跡を元に論文についてその論文中の図の情報をまとめた説明作成のための[MCPサーバ](./mcp)を作成している．
### 提供する tool 一覧
- `create_hash` - 指定したファイルのハッシュ値を計算する
  - Required arguments
    - `filepath` (string): ハッシュ値を計算したいファイルのパス
- `search_target_from_log` - 指定した文字列について，証跡を保存したログから検索する
  - Required arguments
    - `target` (string): 検索したい文字列
- `create_daily_log_file` - 指定した日付の証跡のみを証跡を保存したログから取り出し，ファイルに出力する
  - Required arguments
    - `day` (string): 証跡を取り出したい日付
    - `path` (string): 取り出した証跡の一覧を出力したいファイルのパス

### Configuration
1. Configuration for Claude.app
```json
{
  "mcpServers": {
    "canis": {
      "command": "uv",
      "args": [
      "--directory",
      "/path/of/canis_mcp",
      "run",
      "main.py",
      "/path/of/canis/hash_log"
      ]
    }
  }
}
```

2. Configuration for VS code
```json
{
  "servers": {
    "canis": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/of/canis_mcp",
        "run",
        "main.py",
        "/path/of/canis/hash_log"
      ],
    }
  }
}
```

#### 各パスの説明
- `path/of/canis_mcp` : `canis_mcp` ディレクトリのパス
- `path/of/canis/hash_log` : canisが証跡のログを保存しているファイルのパス

# 参考文献
本システムは，第204回DPS・第109回EIP合同研究発表会で発表した[論文](./docs/IPSJ-DPS25204008.pdf)で提案した内容に基づいた機能を提供している．

ここに掲載した著作物の利用に関する注意 本著作物の著作権は情報処理学会に帰属します。本著作物は著作権者である情報処理学会の許可のもとに掲載するものです。ご利用に当たっては「著作権法」ならびに「情報処理学会倫理綱領」に従うことをお願いいたします。
