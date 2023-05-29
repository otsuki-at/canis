import sys
import os
import signal
from lark import Lark
from lark import Transformer
import time
import pathlib
import redis

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
                print("update!")
                logs = self.fd.read().splitlines()

                return logs
            else:
                print("no update!")
                time.sleep(4)

    def __del__(self):
        self.fd.close()
        print("file closed.")

class LogConverter:
    def __init__(self):
        self.log = Log()

    def convert(self, logs):
        grammar = open("../src/converter/pattern.lark")
        parser = Lark(grammar, parser="lalr", start="log")
        global converted_logs

        for entry in logs:
            self.log.set_log(entry)
            event = self.log.get_event()
            path = self.log.get_path()

            if event=="rename":
                entry = self.log.get_date() + "," + self.log.get_inode() + "," + event + "," + entry.split(',')[4]

            if event in EventList:
                entry = "{" + entry + "}"
                self.log.store_entry(path, entry)
                logs = self.log.get_logs(path)
                try:
                    # tree = parser.parse(logs)
                    #
                    # print(self.log.get_date() + "," + self.log.get_inode() + ",", end="")
                    # LogGenerator().transform(tree)
                    # if event=="rename":
                    #     print("," + path + "," + entry.split(',')[3][0:-1])
                    # else:
                    #     print("," + path)
                    #
                    # self.log.delete_logs(path)
                    tree = parser.parse(logs)

                    converted_logs += self.log.get_date() + "," + self.log.get_inode() + ","
                    LogGenerator().transform(tree)
                    if event=="rename":
                        converted_logs += "," + path + "," + entry.split(',')[3][0:-1] + "\n"
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

def handler(signum, frame):
    os.remove("../tmp/" + pidfile_name)

def main():
    args = sys.argv
    logfile_name = args[1]
    global pidfile_name
    pidfile_name = args[2]
    global converted_logs
    db = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pid_file = open("../tmp/" + pidfile_name, 'w')
    pid = str(os.getpid())
    pid_file.write(pid + '\n')
    pid_file.flush()
    signal.signal(signal.SIGTERM, handler)


    log_converter = LogConverter()
    logfile = LogFile(logfile_name)

    publisher = Publisher()
    while(True):
        logs = logfile.get_update()
        out_logs = log_converter.convert(logs)
        converted_logs = ""
        print(out_logs)
        publisher.publish(out_logs)


if __name__ == "__main__":
    main()
