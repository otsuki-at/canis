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

converted_logs = ""
pidfile_name = ""

EventList = ["create",
             "open",
             "read",
             "write",
             "release",
             "rename",
             "unlink"]

# 構文解析器の実行部
class LogGenerator(Transformer):
    def create(self, tree):
        global converted_logs
        converted_logs += "create"
        # print("create", end="")

    def read(self, tree):
        global converted_logs
        converted_logs += "read"
        # print("read", end="")

    def update(self, tree):
        global converted_logs
        converted_logs += "update"
        # print("update", end="")

    def remove(self, tree):
        global converted_logs
        converted_logs += "remove"
        # print("remove", end="")

    def rename(self, tree):
        global converted_logs
        converted_logs += "rename"
        # print("rename", end="")

class Log:
    def __init__(self):
        self.logs = {}

    def set_log(self, entry):
        self.date = entry.split(',')[0]
        self.inode = entry.split(',')[1]
        self.event = entry.split(',')[2]
        self.path = entry.split(',')[3]

    def get_date(self):
        return self.date

    def get_inode(self):
        return self.inode

    def get_event(self):
        return self.event

    def get_path(self):
        return self.path

    def get_logs(self, path):
        return self.logs[path]

    def store_entry(self, path, entry):
        if path in self.logs.keys():
            logs = self.logs[path]
            self.logs[path] = logs + entry
        else:
            self.logs[path] = entry

    def delete_logs(self, path):
        del self.logs[path]

class LogConverter:
    def __init__(self):
        self.log = Log()

    def convert(self, log_mes):
        grammar = open(dir + "/src/converter/pattern.lark")
        parser = Lark(grammar, parser="lalr", start="log")
        global converted_logs

        self.log.set_log(log_mes)
        event = self.log.get_event()
        path = self.log.get_path()

        if event=="rename":
            log_mes = self.log.get_date() + "," + self.log.get_inode() + "," + event + "," + log_mes.split(',')[4]

        if event in EventList:
            log_mes = "{" + log_mes + "}"
            self.log.store_entry (path, log_mes)
            log_mes = self.log.get_logs(path)
            try:
                tree = parser.parse(log_mes)

                converted_logs += self.log.get_date() + "," + self.log.get_inode() + ","
                LogGenerator().transform(tree)
                if event=="rename":
                    converted_logs += "," + path + "," + log_mes.split(',')[3][0:-1] + "\n"
                else:
                    converted_logs += "," + path + "\n"
                self.log.delete_logs(path)
            except:
                pass
        grammar.close()
        return converted_logs

class Publisher:
    def __init__(self):
        self.rc = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def publish(self, data):
        self.rc.publish("converted_log", data)

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
    global converted_logs
    db = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    pid_file = open(dir + "/tmp/" + pidfile_name, 'w')
    pid = str(os.getpid())
    pid_file.write(pid + '\n')
    pid_file.flush()
    signal.signal(signal.SIGTERM, handler)

    log_converter = LogConverter()

    subscriber = Subscriber()
    publisher = Publisher()

    while(True):
        log_mes = subscriber.listen()
        out_logs = log_converter.convert(log_mes)
        converted_logs = ""
        if out_logs == "":
            continue
        publisher.publish(out_logs)
        with open(logdir + '/converted.log', 'a') as f:
            print(out_logs, file=f)


if __name__ == "__main__":
    main()
