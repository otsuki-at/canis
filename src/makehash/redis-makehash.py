import sys
import os
import signal
import time
import pathlib
from dotenv import load_dotenv
import hashlib
import subprocess
import datetime
import redis

load_dotenv()
dir = os.getenv('DIR')
logdir = os.getenv('LOGDIR')

class Subscriber:
    def __init__(self):
        self.rc = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.ps = self.rc.pubsub()
        self.ps.subscribe("fuse-watch-log")

    def listen(self):
        try:
            for mes in self.ps.listen():
                if mes["data"] == 1:
                    continue
                return mes["data"]
        except:
            sys.exit()

def handler(signum, frame):
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
        log = subscriber.listen()
        time = log.split(',')[0]
        event = log.split(',')[2]
        file_path = log.split(',')[3]

        if(event != "getattr" and event != "read"):
            if os.path.isfile(file_path):
                file_path = file_path.replace('otsuki','otsuki.can',1)
                hash_value = subprocess.run(['sha256sum',file_path], capture_output=True, text=True).stdout
                hash_value = hash_value.replace('otsuki.can','otsuki',1)
                hash_value = hash_value.replace('  ',',',1)
                with open (logdir + '/hash.log', 'a') as f:
                    print(time + ',' + hash_value, end='', file=f)


if __name__ == "__main__":
    main()
