import sys
import os
import signal
import time
import pathlib
from dotenv import load_dotenv
import hashlib
import subprocess
import datetime

load_dotenv()
dir = os.getenv('DIR')
logdir = os.getenv('LOGDIR')

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

def handler(signum, frame):
    os.remove(dir + "/tmp/" + pidfile_name)
    sys.exit()

def main():
    args = sys.argv
    logfile_name = args[1]
    global pidfile_name
    pidfile_name = args[2]
    pid_file = open(dir + "/tmp/" + pidfile_name, 'w')
    pid = str(os.getpid())
    pid_file.write(pid + '\n')
    pid_file.flush()
    signal.signal(signal.SIGTERM, handler)

    logfile = LogFile(logfile_name)

    while(True):
        logs = logfile.get_update()
        for entry in logs:
            time = entry.split(',')[0]
            event = entry.split(',')[2]
            file_path = entry.split(',')[3]

            if(event != "getattr" and event != "read"):
                if os.path.isfile(file_path):
                    file_path = file_path.replace('otsuki','otsuki.can',1)
                    hash_value = subprocess.run(['sha256sum',file_path], capture_output=True, text=True).stdout
                    hash_value = hash_value.replace('otsuki.can','otsuki',1)
                    with open (logdir + '/hash.log', 'a') as f:
                        now = datetime.datetime.now()
                        print(time + ',' + hash_value, end='', file=f)
                # with open(file_path, 'rb') as file:
                #     file_data = file.read()
                # hash_value = hashlib.sha256(file_data)
                # with open(logdir + '/hash.log', 'a') as f:
                #     print(time,file_path,hash_value.hexdigest(), file=f)

            # path = entry.split(',')[3]
            # if os.path.isfile(path):
            #     file_path = path.(' ','/ ')
            #     hash_file
            #     os.system("sha256sum " + path + "> /home/log/trigora/hash/" +path.replace('/','.') +".txt")

if __name__ == "__main__":
    main()
