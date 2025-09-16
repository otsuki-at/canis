# Technical Memo
## ディレクトリ構成
+ リポジトリ内の各ファイルの説明を述べる．
```
.
├── README.md
├── bin
│   ├── canis
│   └── upload
├── log
├── src
│   ├── collector
│   │   ├── collector.c
│   │   └── collector_helpers.h
│   ├── converter
│   │   ├── converter.py
│   │   └── return-converter.py
│   ├── gethistory
│   │   └── gethistory.py
│   └── makehash
│        └── makehash.py
├── mcp
│   ├── README.md
│   └── main.py
└── tmp
```

+ 主要なディレクトリ/ファイルの一覧を示す．
  + 各ディレクトリの中身は後述．

|通番|ディレクトリ/ファイル名|説明|
|---|---|---|
|1|bin/|システムの実行ファイル `canis` を配置している．|
|2|log/|canis のシステムログが作成される．|
|3|src/|FS監視部，履歴変換部，ハッシュ作成部を管理している．|
|4|mcp/|説明作成機能を提供するMCPサーバを管理している．|
|5|tmp/|`canis` の実行中に生成される一時ファイルが保存される．|

## bin/
### ファイル一覧
+ `canis`
+ `upload`

### `canis`
+ システムを運用するシェルスクリプト．
+ `canis start` でシステムを起動，`canis stop` でシステムを停止できる．
+ `canis info` でハッシュを検索できる．

### `upload`
+ 日次ハッシュを作成し，公開するシェルスクリプト．

## `src/`
### ファイル一覧
+ `collector/`
+ `converter/`
+ `gethistory/`
+ `makehash/`

### `collector/`
+ FS監視部の本体 `collector.c` を配置している．
+ 実行するには `libfuse` のインストールが必要．

### `converter/`
+ 履歴変換部の本体 `converter.py` および取得した履歴をそのまま返す `return-converter.py` を配置している．
+ 現在は， `converter.py` において，一部のエディタでファイル編集を行った際に履歴変換できない問題がある．

### `gethistory/`
+ 取得したファイルアクセス履歴を履歴変換部に送信する `gethistory.py` を配置している．

### `makehash/`
+ ハッシュ作成部の本体 `makehash.py` を配置している．

## `mcp/`
### ファイル一覧
+ `README.md`
+ `main.py`

### `README.md`
+ 説明作成機能のための MCPサーバに関する利用方法を記載している．

### `main.py`
+ MCP サーバの本体となるファイル．

## `tmp/`
+ 履歴変換部と実行部のプロセス管理用の一時ファイルが生成される．
