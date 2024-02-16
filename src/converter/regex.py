import re
import sys

class Converter:
    def convert(self, logs):

        for i, log in enumerate(logs):
            s_log = log.split(',')
            date = s_log[0]
            inode = s_log[1]
            event = s_log[2]
            path = s_log[3]

            match event:
                case "create":
                    m = re.search(r'create,'+path+'.*'+'(\d{4}-\d+-\d+T\d+:\d+:\d+\.\d+,\d+)'+',release,'+path, ''.join(logs[i:]))
                    if m:
                        print(m.group(1) + ",create," + path)
                case "open":
                    # m = re.search(r'open,'+path+'.+'+'read,'+path+'.*'+'(\d{4}-\d+-\d+T\d+:\d+:\d+\.\d+,\d+)'+',release,'+path, ''.join(logs[i:]))
                    # if m:
                    #     print(m.group(1) + ",read," + path)
                    #
                    m = re.search(r'open,'+path+'.+'+'write,'+path+'.*'+'(\d{4}-\d+-\d+T\d+:\d+:\d+\.\d+,\d+)'+',release,'+path, ''.join(logs[i:]))
                    if m:
                        print(m.group(1) + ",update," + path)
                case "unlink":
                    print(date + ',' + inode + ',remove,' + path)
                case "rename":
                    print(date + ',' + inode + ',rename,' + path)

class InteravticeConverter:
    def __init__(self):
        self.stat = {}

    def feed_log(self, logs):

        for i, log in enumerate(logs):
            s_log = log.split(',')
            date = s_log[0]
            inode = s_log[1]
            event = s_log[2]
            path = s_log[3]


            match event:
                case "create":
                    m = re.search(r'create,'+path+'.*'+'(\d{4}-\d+-\d+T\d+:\d+:\d+\.\d+,\d+)'+',release,'+path, ''.join(logs[i:]))
                    if m is None:
                        self.stat[path] = "create"
                    else:
                        print(m.group(1) + ",create," + path)
                        del self.stat[path]
                case "open":
                    # m = re.search(r'open,'+path+'.+'+'read,'+path+'.*'+'(\d{4}-\d+-\d+T\d+:\d+:\d+\.\d+,\d+)'+',release,'+path, ''.join(logs[i:]))
                    # if m:
                    #     print(m.group(1) + ",read," + path)
                    #
                    m = re.search(r'open,'+path+'.+'+'write,'+path+'.*'+'(\d{4}-\d+-\d+T\d+:\d+:\d+\.\d+,\d+)'+',release,'+path, ''.join(logs[i:]))
                    if m:
                        print(m.group(1) + ",update," + path)
                case "unlink":
                    print(date + ',' + inode + ',remove,' + path)
                case "rename":
                    print(date + ',' + inode + ',rename,' + path)

    def get_stat(self):
        print(self.stat)


def main():
    args = sys.argv
    # logfile_name = args[1]

    # fd = open(logfile_name)
    # logs = fd.read().splitlines()

    # converter = Converter()
    # converter.convert(logs)

    # i_converter = InteravticeConverter()
    # i_converter.feed_log(["2023-10-08T23:55:22.282198,0,create,/home/mukohara/testfile","2023-10-08T23:55:22.282198,0,getattr,/home/mukohara/testfile"])
    # i_converter.get_stat()
    # print("1")
    # i_converter.feed_log(["2023-10-08T23:55:22.282198,0,release,/home/mukohara/testfile"])



if __name__ == "__main__":
    main()
