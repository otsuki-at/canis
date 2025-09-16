import sys
import os
import signal
from lark import Lark
from lark import Transformer
import time
from datetime import datetime
import pathlib
import redis
from dotenv import load_dotenv
import subprocess

load_dotenv()
dir = os.getenv('DIR')
logdir = os.getenv('LOGDIR')

pidfile_name = ""

class LogFile:
    def __init__(self, logfile_name):
        self.filename = logfile_name
        self.f = pathlib.Path(self.filename)
        self.lastdate = None
        self.fd = open(self.filename, "r")
        self.last_position = 0  # 前回の読み取り位置を追跡

    def update_exists(self):
        lastmdate = self.f.stat().st_mtime
        if self.lastdate != lastmdate:
            self.lastdate = lastmdate
            return True
        return False

    def get_update(self):
        while True:
            if self.update_exists():
                self.fd.seek(self.last_position)  # 前回の位置から読み取る
                new_data = self.fd.read()  # 新たに追記された部分を全て取得
                if not new_data:
                    time.sleep(4)
                    continue

                logs = new_data.splitlines(keepends=True)

                # 最後の行が不完全なら、その行を取り除いて次回処理する準備
                if logs and not logs[-1].endswith("\n"):
                    incomplete_line = logs.pop(-1)  # 不完全な行を取り除く
                    self.last_position = self.fd.tell() - len(incomplete_line)

                else:
                    # 完全な行が処理された場合は、位置を更新
                    self.last_position = self.fd.tell()
                # 完全な行だけを返す
                return [line.strip() for line in logs]
            else:
                time.sleep(8)

    def __del__(self):
        self.fd.close()

class Publisher:
    def __init__(self):
        self.rc = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def publish(self, data):
        self.rc.publish("fuse-watch-log", data)

def handler(signum, frame):
    os.remove(dir + "/tmp/" + pidfile_name)
    sys.exit()

def main():
    args = sys.argv
    logfile_name = args[1]
    global pidfile_name
    pidfile_name = args[2]
    global converted_logs

    pid_file = open(dir + "/tmp/" + pidfile_name, 'w')
    pid = str(os.getpid())
    pid_file.write(pid + '\n')
    pid_file.flush()
    signal.signal(signal.SIGTERM, handler)

    # ログを取得するファイルを設定
    logfile = LogFile(logfile_name)

    # ログを出力するRedisを設定
    publisher = Publisher()

    while(True):
        logs = logfile.get_update()
        for log in logs:
            publisher.publish(log)

if __name__ == "__main__":
    main()
