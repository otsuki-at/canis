# Technical Memo
## ディレクトリ構成
+ リポジトリ内の各ファイルの説明を述べる．
```
.
├── README.md
├── bin
│   ├── recentfiles
│   │   ├── recentfiles
│   │   └── recentfiles.c
│   └── trigora
├── conf
│   └── actions
│       ├── action1.exmaple.yaml
│       ├── action2.exmaple.yaml
│       └── actions.conf.yaml
├── log
├── src
│   ├── collector
│   │   ├── collector.c
│   │   └── collector_helpers.h
│   ├── converter
│   │   ├── converter.py
│   │   ├── pattern.lark
│   │   └── regex.py
│   └── executor
│       └── executor.py
└── tmp
```

+ 主要なディレクトリ/ファイルの一覧を示す．
  + 各ディレクトリの中身は後述．

|通番|ディレクトリ/ファイル名|説明|
|---|---|---|
|1|bin/|システムの実行ファイル `trigora` を配置している．|
|2|conf/actions/|`executor.py` の設定ファイルを配置する．|
|3|log/|trigora のシステムログや `collector.py` が出力したファイルアクセス履歴が作成される．|
|4|src/|FS監視部，履歴変換部，実行部のソースコードを管理している．|
|5|tmp/|`trigora` の実行中に生成される一時ファイルが保存される．|
|6|requirements.txt|システムの動作に必要な Python のパッケージ一覧が記述されている．|

## bin/
### ファイル一覧
+ `trigora`
+ `recentfiles/`

### `trigora`
+ システムを運用するシェルスクリプト．
+ `trigora start` でシステムを起動，`trigora stop` でシステムを停止できる．

### `recentfiles/`
+ `refentfiles` コマンドを管理しているディレクトリ．なお，コマンドは未完成．
+ コマンドの機能は，履歴変換部が DB に登録した履歴の一覧からフィルタリングしてファイル一覧を出力すること．
+ フィルタリングの項目は，ファイルアクセス種別，期間，拡張子などを想定．
+ 例として，`recentfiles -t read -n 60 '*.txt'` と実行した場合は，ファイル参照の履歴で，今日から60日前までの履歴のうち，`.txt` の拡張子を持つファイル一覧を出力する．

## `conf/actions/`
### ファイル一覧
+ `action1.example.yaml`
+ `action2.example.yaml`
+ `actions.conf.yaml`

### `action1.example.yaml`，`action2.example.yaml`
+ 自動実行処理の設定ファイルの例．
+ `actions.conf.yaml` から指定される．

### `actions.conf.yaml`
+ 自動実行処理の設定ファイルのうち，有効にするものを指定する設定ファイル．

## `log/`
+ FS監視部が収集したファイルアクセス履歴と履歴変換部が変換したファイル操作履歴，`trigora` が出力するシステムログが保存される．
+ ファイルアクセス履歴は `fuse-watch.log`，ファイル操作履歴は `converted.log`，システムログは `trigora.log` というファイルに出力される．

## `src/`
### ファイル一覧
+ `collector/`
+ `converter/`
+ `executor/`
+ `clustering`

### `collector/`
+ FS監視部の本体 `collector.c` を配置している．
+ 実行するには `libfuse` のインストールが必要．

### `converter/`
+ 履歴変換部の本体 `converter.py` を配置している．
+ `pattern.lark` は，解析ライブラリ `Lark` が使用する文法．
+ `regex.py` は，正義表現を用いた履歴変換プログラム．未完成．

### `executor/`
+ 実行部の本体 `executor.py` を配置している．

### `clustering`
+ `clustering.py` と `heatmap.py` を配置している．
+ `clustering.py` は，それぞれ特定の作業から得られたファイルアクセス履歴のファイルを複数コマンドライン引数にとり，特徴量を抽出して k-means 法によりクラスタリングを行うプログラム．
+ `heatmap.py` は，ファイルアクセス履歴のファイルを1つ引数にとり，様々な拡張子を持つファイルやドットファイルへのアクセス回数を5秒間隔で時系列に取得しヒートマップとして出力する．

## `tmp/`
+ 履歴変換部と実行部のプロセス管理用の一時ファイルが生成される．
