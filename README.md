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
+ `action.conf` に，処理を設定する．
  ```
  [rule]
  PATH = /path/of/target/file
  WHEN = event_name
  DO = gcc /path/of/target/file
  ```
  + PATH には，監視対象ファイルのパスを記述する．
    `,` 区切りで複数のファイルを指定可能．また，`*` をワイルドカードとして指定可能．
  + WHEN には，監視対象のファイル操作を記述する．
    `,` 区切りで複数のファイル操作を指定可能．指定可能なファイル操作は，`create`，`update`，`read`，`remove`，`rename`．
  + DO には，実行する処理を記述する．
    CLI で実行するコマンドを記述する．`,` 区切りで複数のコマンドを指定可能．

## Launch
+ システム有効化
  `$ trigora start`
+ システム無効化
  `$ trigora stop`
