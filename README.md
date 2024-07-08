# Trigora
本システムは，計算機上でのユーザのファイル操作をリアルタイムに監視し，監視の結果出力されたファイル操作履歴に対応してあらかじめ設定した処理を自動で実行するシステムである．設定する項目は，PATH (どのファイルが)，WHEN (どんなファイル操作を受けた時)，DO (どのような処理を実行する) である．

 "Trigora"は，"Trigger"をもとに作られた造語であり，"Gora"は，スペイン語で「山」を意味する言葉である．この名前は，スタートや起点を示す「トリガー」と，高みを目指すという意味を込めた「山」という言葉を組み合わせたものである．Trigoraは，ファイル操作を起点にして，ユーザーのビジネスや生活の質を向上させることを目指したシステムである．

# Requirements
+ Python 3.x
+ Redis
+ [libfuse3.11.0](https://github.com/libfuse/libfuse)

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
1. Trigora で監視するディレクトリ以外の場所にログファイルを保存するディレクトリを作成する．以下の例では/home以下に作成したため，ディレクトリの所有者を変更している．
  ```
  $ cd /home
  $ sudo mkdir log
  $ sudo chown $USER log
  $ sudo chgrp $USER log
  ```

### 環境変数の設定
1. 以下の2つのパスについて記述した.envファイルを作成する．
  + DIR には Trigora を保存したディレクトリのパスを定義する．
  + LOGDIR にはログファイルを格納するために作成したディレクトリのパスを定義する．
2. bin/trigora 中の ENVDIR 変数に .env ファイルのパスに変更する．
  ```
  # .envファイルのパスを設定する．
  ENVDIR=/path/of/.env
  ```
3. ファイルに対する操作を fuse-watch.log に記述しないファイルが存在する場合は， .env ファイルに以下のような形式で追加する．2つ以上設定したい場合は， IGNORE1 のようにし，それ以降も IGNORE2, ... のように定義する．
  ```
  IGNORE0=/user.can/path/of/ignore0
  ```

### 自動実行処理の設定
1. `conf/actions/` に，自動実行したい処理の設定を記述した YAML ファイルを作成する．
  ```
  path: /path/of/target/file
  when: event_name
  do: gcc /path/of/target/file
  ```
  + path には，監視対象ファイルのパスを記述する．
    `,` 区切りで複数のファイルを指定可能．また，`*` をワイルドカードとして指定可能．
  + when には，監視対象のファイル操作を記述する．
    `,` 区切りで複数のファイル操作を指定可能．指定可能なファイル操作は，`create`，`update`，`read`，`remove`，`rename`．
  + do には，実行する処理を記述する．
    CLI で実行するコマンドを記述する．
2. `conf/actions/actions.conf.yaml` で，使用する設定ファイルを指定する．
  ```
  actions:
    - action1.example.yaml
    - action2.example.yaml
  ```

## Launch
以下のように実行するには，`bin/trigora` にパスを通す必要がある．
+ システム有効化
  `$ trigora start`
+ システム無効化
  `$ trigora stop`

## Clustering file access log
ファイルアクセス履歴が出力された複数のファイルをクラスタリングする．ファイルは，それぞれ分類したい作業に対応したファイルである．ファイルアクセス履歴は，システムを有効化した後，随時 `log/fuse-watch.log` に出力される．
2つのコーディング作業と1つのウェブブラウジングのファイルアクセス履歴をクラスタリングする例を以下に示す．
```
$ python clustering.py coding1.log coding2.log browsing1.log
```
分類するクラスタ数に応じて，`clustering.py` 565行目の `KMeans` メソッドの引数 `n_clusters` の値を変更する．例えば上記の例において，コーディング作業とウェブブラウジングに分類したい場合は，以下のように `n_cluster=2` とする．
```
kmeans = KMeans(n_clusters=2, max_iter=400, init="random", n_init="auto")
```

## Creating Heat Map of file access
ファイルアクセス履歴が出力されたファイルをヒートマップとして出力する．ファイルアクセス履歴を任意の時間間隔で分割し，それぞれの間隔で様々な拡張子を持つファイルやドットファイルへのアクセス回数を集計しヒートマップとして出力する．
Python を用いたコーディング作業により得られたファイルアクセス履歴をヒートマップ化する実行例と得られたヒートマップを以下に示す．
```
$ python heatmap.py coding1.log
```
<img src="https://github.com/mukohara/trigora/assets/81736636/87eb08e6-f1cf-455c-ba2d-0a0d4708e90b" width="500px">

ファイルアクセス履歴の分割時間間隔は，`heatmap.py` 563行目の `separate_by_time(5)` メソッドのように指定する．この場合は5秒間隔で分割を行う．また，ヒートマップのタイトルなどは `Heatmap` クラスの `show(self, matrix)` メソッドで指定する．
