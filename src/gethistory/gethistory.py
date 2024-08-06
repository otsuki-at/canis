import sys
import os
import signal
from lark import Lark
from lark import Transformer
import time
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
        self.fd = open(self.filename)

    def update_exists(self):
        lastmdate = self.f.stat().st_mtime

        if self.lastdate != lastmdate:
            self.lastdate = lastmdate
            return True
        else:
            return False

    def get_update(self):
        while(True):
            if self.update_exists():
                logs = self.fd.read().splitlines()

                return logs
            else:
                time.sleep(4)

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
    db = redis.Redis(host='localhost', port=6379, decode_responses=True)

    pid_file = open(dir + "/tmp/" + pidfile_name, 'w')
    pid = str(os.getpid())
    pid_file.write(pid + '\n')
    pid_file.flush()
    signal.signal(signal.SIGTERM, handler)

    logfile = LogFile(logfile_name)

    publisher = Publisher()
    while(True):
        logs = logfile.get_update()
        for log in logs:
            publisher.publish(log)
            with open(logdir + '/history.log', 'a') as f:
                print(log, file=f)

if __name__ == "__main__":
    main()
