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
            print("redis finish")
            sys.exit()

class Publisher:
    def __init__(self):
        self.rc = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def publish(self, data):
        self.rc.publish("converter-log", data)

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
    publisher = Publisher()

    while(True):
        log = subscriber.listen()
        event = log.split(',')[2]
        file_path = log.split(',')[3]
        if(event != "getattr" and event != "read"):
            if os.path.isfile(file_path): # パスがファイルかどうか確かめる
                publisher.publish(log)

if __name__ == "__main__":
    main()
