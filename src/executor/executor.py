import redis
import sys
import os
import signal

pidfile_name = ""

class Subscriber:
    def __init__(self):
        self.rc = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.ps = self.rc.pubsub()
        self.ps.subscribe("converted_log")

    def listen(self):
        try:
            for mes in self.ps.listen():
                if mes["data"] == 1:
                    continue
                return mes["data"]
        except:
            sys.exit()

class Processor:
    def __init__(self, filepath):
        self.fd = open(filepath)
        self.conf = []
        self.i = 0

        params = self.fd.read().splitlines()
        for param in params:
            if param.startswith("path"):
                self.conf.append({"path": param[6:-1]})
            elif param.startswith("when"):
                self.conf[self.i].update({"when": param[6:-1]})
            elif param.startswith("do"):
                self.conf[self.i].update({"do": param[4:-1]})
                self.i += 1

    def process(self, data):
        logs = data.split("\n")

        for log in logs:
            if log == "":
                continue

            event = log.split(",")[2]
            path = log.split(",")[3]

            list_search = list(filter(lambda item : item["path"] == path, self.conf))
            for entry_search in list_search:
                if entry_search["when"] == event:
                    os.system(entry_search["do"])

    def __del__(self):
        self.fd.close()

def handler(signum, frame):
    os.remove("../tmp/" + pidfile_name)

def main():
    args = sys.argv
    configfile_name = args[1]
    global pidfile_name
    pidfile_name = args[2]
    pid_file = open('../tmp/' + pidfile_name, 'w')
    pid = str(os.getpid())
    pid_file.write(pid + '\n')
    pid_file.flush()
    signal.signal(signal.SIGTERM, handler)

    subscriber = Subscriber()
    processor = Processor(configfile_name)
    while(True):
        mes = subscriber.listen()

        processor.process(str(mes))

if __name__ == "__main__":
    main()
