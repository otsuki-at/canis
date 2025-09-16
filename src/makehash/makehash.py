import sys
import os
import signal
import time
from datetime import datetime,timezone
import pathlib
from dotenv import load_dotenv
import hashlib
import subprocess
import redis

load_dotenv()
dir = os.getenv('DIR')
logdir = os.getenv('LOGDIR')

class Subscriber:
    def __init__(self):
        self.rc = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.ps = self.rc.pubsub()
        self.ps.subscribe("converter-log")

    def listen(self):
        try:
            for mes in self.ps.listen():
                if mes["data"] == 1:
                    continue
                return mes["data"]
        except:
            print("redis finish")
            sys.exit()

def handler(signum, frame):
    print("killed process")
    os.remove(dir + "/tmp/" + pidfile_name)
    sys.exit()

def main():
    args = sys.argv

    global pidfile_name
    pidfile_name = args[1]
    pid_file = open(dir + "/tmp/" + pidfile_name, 'w')
    pid = str(os.getpid())
    pid_file.write(pid + '\n')
    pid_file.flush()
    signal.signal(signal.SIGTERM, handler)

    subscriber = Subscriber()

    while(True):
        log = subscriber.listen() # ログをRedisから取得
        logtime = log.split(',')[0]
        file_path = log.split(',')[3]

        file_path = file_path.replace('otsuki','otsuki.can',1) # ハッシュ作成時に利用するパスをFUSEで監視しないパスに変更
        hash_value = subprocess.run(['sha256sum',file_path], capture_output=True, text=True).stdout # ハッシュを作成
        hash_value = hash_value.replace('otsuki.can','otsuki',1)
        hash_value = hash_value.replace('  ',',',1)

        with open (logdir + '/hash.log', 'a') as f:
            print(logtime + ',' + hash_value, end="", file =f)

if __name__ == "__main__":
    main()
