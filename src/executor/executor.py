import redis
import sys
import os
import signal
import yaml

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
        # self.fd = open(filepath)
        self.action_confs = []
        # self.i = 0
        with open(filepath, 'r') as actions_conf_yml:
            action_confs = yaml.safe_load(actions_conf_yml)

        # print(action_confs["actions"])

        for action_conf in action_confs["actions"]:
            with open("../conf/actions/" + action_conf, "r") as action:
                conf = yaml.safe_load(action)
                self.action_confs.append([conf["path"], conf["when"], conf["do"]])

        # params = self.fd.read().splitlines()
        # print(params)
        # for param in params:
        #     if param.startswith("path"):
        #         self.conf.append({"path": param[6:-1]})
        #     elif param.startswith("when"):
        #         self.conf[self.i].update({"when": param[6:-1]})
        #     elif param.startswith("do"):
        #         self.conf[self.i].update({"do": param[4:-1]})
        #         self.i += 1

    def process(self, data):
        logs = data.split("\n")

        for log in logs:
            if log == "":
                continue

            event = log.split(",")[2]
            path = log.split(",")[3]

            # list_search = list(filter(lambda item : item["path"] == path, self.conf))
            # for entry_search in list_search:
            #     if entry_search["when"] == event:
            #         os.system(entry_search["do"])
            for conf in self.action_confs:
                conf_path = conf[0]
                conf_when = conf[1]
                conf_do = conf[2]
                if (conf_path == path) and (conf_when == event):
                    os.system(conf_do)

    # def __del__(self):
    #     self.fd.close()

def handler(signum, frame):
    os.remove("../tmp/" + pidfile_name)
    sys.exit()

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
