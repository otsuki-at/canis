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
+ システム有効化
  `$ trigora start`
+ システム無効化
  `$ trigora stop`
