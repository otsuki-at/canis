import re
import sys


def main():
    args = sys.argv
    logfile_name = args[1]

    fd = open(logfile_name)
    logs = fd.read().splitlines()

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


if __name__ == "__main__":
    main()
