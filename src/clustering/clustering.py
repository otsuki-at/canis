from os import copy_file_range
import numpy as np
import time
import pathlib
import sys
from datetime import datetime, timedelta
import seaborn as sns
from sklearn.cluster import KMeans
import codecs
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import StrMethodFormatter

from sklearn.metrics.pairwise import normalize

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
        self.fd = codecs.open(self.filename, 'r', 'utf-8', 'ignore')

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
                # print("update!")
                logs = self.fd.read().splitlines()

                return logs
            else:
                # print("no update!")
                time.sleep(4)

    def __del__(self):
        self.fd.close()

class Feature:
    def set_logfile(self, logfile_name, end=-1):
        self.filename = logfile_name
        self.f = pathlib.Path(self.filename)
        self.lastdate = None
        self.fd = codecs.open(self.filename, 'r', 'utf-8', 'ignore')
        self.logs = self.fd.read().splitlines()[:end]

    def get_feature(self):
        feature = []
        entry_cnt = self.entry_cnt()
        event_cnt = self.event_cnt()

        program_ext_cnt_all = self.program_extension_all()
        document_ext_cnt_all = self.document_extension_all()
        program_ext_cnt_ratio = self.program_extension_cnt_ratio()
        document_ext_cnt_ratio = self.document_extension_cnt_ratio()
        program_ext_ratio = self.program_ext_ratio()
        document_ext_ratio = self.document_ext_ratio()
        firefox_cnt = self.firefox_cnt()
        chrome_cnt = self.chrome_cnt()
        browsing_feature = [firefox_cnt[0] + chrome_cnt[0]]
        dotfile_cnt_ratio = self.dotfile_cnt_ratio()

        return program_ext_cnt_ratio + document_ext_cnt_ratio + dotfile_cnt_ratio

    def get_norm_feature(self, features):
        normalized = []
        ret = []
        el_cnt = len(features)
        f_cnt = len(features[0])

        for i in range(f_cnt):
            feature_col = [r[i] for r in features]
            if not any(num != 0 for num in feature_col):
                normalized.append([0] * el_cnt)
                continue
            max_el = max(feature_col)
            min_el = min(feature_col)
            normalized_col = []
            for el in feature_col:
                normalized_col.append((el - min_el)/(max_el - min_el))

            normalized.append(normalized_col)

        for i in range(len(normalized[0])):
            ret.append([r[i] for r in normalized])

        return ret

    def event_cnt(self):
        init_cnt = getattr_cnt = access_cnt = readlink_cnt = readdir_cnt= mknod_cnt = mkdir_cnt = symlink_cnt = unlink_cnt = rmdir_cnt = rename_cnt = link_cnt = chmod_cnt = chown_cnt = truncate_cnt = utimens_cnt = open_cnt = create_cnt = read_cnt = write_cnt = statfs_cnt = release_cnt = fsync_cnt = fallocate_cnt = setxattr_cnt = getxattr_cnt = listxattr_cnt = removexattr_cnt = copy_file_range_cnt = lseek_cnt = 0

        for log in self.logs:
            event = log.split(",")[2]
            if event == "init":
                init_cnt += 1
            elif event == "getattr":
                getattr_cnt += 1
            elif event == "access":
                access_cnt += 1
            elif event == "readlink":
                readlink_cnt += 1
            elif event == "readdir":
                readdir_cnt += 1
            elif event == "mknod":
                mknod_cnt += 1
            elif event == "mkdir":
                mkdir_cnt += 1
            elif event == "symlink":
                symlink_cnt += 1
            elif event == "unlink":
                unlink_cnt += 1
            elif event == "rmdir":
                rmdir_cnt += 1
            elif event == "rename":
                rename_cnt += 1
            elif event == "link":
                link_cnt += 1
            elif event == "chmod":
                chmod_cnt += 1
            elif event == "chown":
                chown_cnt += 1
            elif event == "truncate":
                truncate_cnt += 1
            elif event == "utimens":
                utimens_cnt += 1
            elif event == "open":
                open_cnt += 1
            elif event == "create":
                create_cnt += 1
            elif event == "read":
                read_cnt += 1
            elif event == "write":
                write_cnt += 1
            elif event == "statfs":
                statfs_cnt += 1
            elif event == "release":
                release_cnt += 1
            elif event == "fsync":
                fsync_cnt += 1
            elif event == "fallocate":
                fallocate_cnt += 1
            elif event == "setxattr":
                setxattr_cnt += 1
            elif event == "getxattr":
                getxattr_cnt += 1
            elif event == "listxattr":
                listxattr_cnt += 1
            elif event == "removexattr":
                removexattr_cnt += 1
            elif event == "copy_file_range":
                copy_file_range_cnt += 1
            elif event == "lseek":
                lseek_cnt += 1

        return [init_cnt, getattr_cnt, access_cnt, readlink_cnt, readdir_cnt, mknod_cnt, mkdir_cnt, symlink_cnt, unlink_cnt, rmdir_cnt, rename_cnt, link_cnt, chmod_cnt, chown_cnt, truncate_cnt, utimens_cnt, open_cnt, create_cnt, read_cnt, write_cnt, statfs_cnt, release_cnt, fsync_cnt, fallocate_cnt, setxattr_cnt, getxattr_cnt, listxattr_cnt, removexattr_cnt, copy_file_range_cnt, lseek_cnt]


    def entry_cnt(self):
        cnt = 0
        for line in self.logs:
            cnt += 1

        return [cnt]

    # time lag between head and tail log
    def ht_timelag(self):
        pass

    def max_min_timelag(self):
        pass

    # count of filepath (excluding duplicates)
    def filepath_cnt(self):
        pass

    def frequent_extension(self):
        pass

    def variously_accessed_file(self):
        pass

    def program_extension_all(self):
        ext_cnt = 0
        ext_list = ["py", "rb", "c", "rs", "js", "cpp", "java", "class", "jar", "pl", "pm", "php", "cgi"]
        ext_group = set(ext_list)

        for log in self.logs:
            path = log.split(",")[3]
            ext = path.rsplit(".")[-1]

            if ext in ext_group:
                ext_cnt += 1

        return [ext_cnt]

    def program_extension_cnt_ratio(self):
        py_cnt = rb_cnt = c_cnt = rs_cnt = js_cnt = cpp_cnt = java_cnt = class_cnt = jar_cnt = pl_cnt = pm_cnt = php_cnt = cgi_cnt = 0
        entry_cnt = 0

        for log in self.logs:
            path = log.split(",")[3]
            ext = path.rsplit(".")[-1]
            entry_cnt += 1

            if ext == "py":
                py_cnt += 1
            elif ext == "rb":
                rb_cnt += 1
            elif ext == "c":
                c_cnt += 1
            elif ext == "rs":
                rs_cnt += 1
            elif ext == "js":
                js_cnt += 1
            elif ext == "cpp":
                cpp_cnt += 1
            elif ext == "java":
                java_cnt += 1
            elif ext == "class":
                class_cnt += 1
            elif ext == "jar":
                jar_cnt += 1
            elif ext == "pl":
                pl_cnt += 1
            elif ext == "pm":
                pm_cnt += 1
            elif ext == "php":
                php_cnt += 1
            elif ext == "cgi":
                cgi_cnt += 1

        return [x / entry_cnt for x in[py_cnt, rb_cnt, c_cnt, rs_cnt, js_cnt, cpp_cnt, java_cnt, class_cnt, jar_cnt, pl_cnt, pm_cnt, php_cnt, cgi_cnt]]

    def document_extension_all(self):
        ext_cnt = 0
        ext_list = ["txt", "tex", "md", "org"]
        ext_group = set(ext_list)

        for log in self.logs:
            path = log.split(",")[3]
            ext = path.rsplit(".")[-1]

            if ext in ext_group:
                ext_cnt += 1

        return [ext_cnt]

    def document_extension_cnt_ratio(self):
        txt_cnt = tex_cnt = md_cnt = org_cnt = 0
        entry_cnt = 0

        for log in self.logs:
            path = log.split(",")[3]
            ext = path.rsplit(".")[-1]
            entry_cnt += 1

            if ext == "txt":
                txt_cnt += 1
            elif ext == "tex":
                tex_cnt += 1
            elif ext == "md":
                md_cnt += 1
            elif ext == "org":
                org_cnt += 1

        return [x / entry_cnt for x in [txt_cnt, tex_cnt, md_cnt, org_cnt]]

    def program_ext_ratio(self):
        ext_cnt = 0
        entry_cnt = 0
        ext_list = ["py", "rb", "c", "rs", "js", "cpp", "java", "class", "jar", "pl", "pm", "php", "cgi"]
        ext_group = set(ext_list)

        for log in self.logs:
            path = log.split(",")[3]
            ext = path.rsplit(".")[-1]
            entry_cnt += 1

            if ext in ext_group:
                ext_cnt += 1

        return [ext_cnt / entry_cnt]

    def document_ext_ratio(self):
        ext_cnt = 0
        entry_cnt = 0
        ext_list = ["txt", "tex", "md", "org"]
        ext_group = set(ext_list)

        for log in self.logs:
            path = log.split(",")[3]
            ext = path.rsplit(".")[-1]
            entry_cnt += 1

            if ext in ext_group:
                ext_cnt += 1

        return [ext_cnt / entry_cnt]

    def firefox_cnt(self):
        firefox_cnt = 0

        for log in self.logs:
            path = log.split(",")[3]

            if "firefox" in path:
                firefox_cnt += 1

        return [firefox_cnt]

    def chrome_cnt(self):
        chrome_cnt = 0

        for log in self.logs:
            path = log.split(",")[3]

            if "google-chrome" in path:
                chrome_cnt += 1

        return [chrome_cnt]

    def dotfile_cnt_ratio(self):
        entry_cnt = 0
        dotfile_cnt = 0

        for log in self.logs:
            files = log.split(",")[3].split("/")
            entry_cnt += 1

            for file in files:
                if file.startswith("."):
                    dotfile_cnt += 1


        return [dotfile_cnt / entry_cnt]

    def get_access_matrix(self):
        el_list = ["py", "rb", "c", "rs", "js", "cpp", "java", "class", "jar", "pl", "pm", "php", "cgi", "txt", "tex", "md", "org"]
        access_matrix = []
        for log in self.logs:
            onehot_vec = [0] * (len(el_list) + 1)
            path = log.split(",")[3]
            ext = path.rsplit(".")[-1]
            files = path.split("/")

            for i, el in enumerate(el_list):
                if ext == el:
                    onehot_vec[i] = 1

            for file in files:
                if file.startswith("."):
                    onehot_vec[-1] = 1

            access_matrix.append(onehot_vec)

        return access_matrix

    def separate_by_time(self, utime):
        separated_logs = []
        log_unit = []
        start_time = datetime.strptime(self.logs[0].split(",")[0], "%Y-%m-%dT%H:%M:%S.%f").timestamp()

        for log in self.logs:
            date = log.split(",")[0]
            time = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
            seconds = time.timestamp()

            if (seconds - start_time) < utime:
                log_unit.append(log)
            else:
                start_time = seconds
                separated_logs.append(log_unit.copy())
                log_unit.clear()
                log_unit.append(log)
        else:
            separated_logs.append(log_unit.copy())

        return separated_logs

    def aggregate_filetype(self, matrix):
        entry_cnt = 0
        aggregates = []

        for log_unit in matrix:
            py_cnt = rb_cnt = c_cnt = rs_cnt = js_cnt = cpp_cnt = java_cnt = class_cnt = jar_cnt = pl_cnt = pm_cnt = php_cnt = cgi_cnt = txt_cnt = tex_cnt = md_cnt = org_cnt = dotfile_cnt = 0

            for log in log_unit:
                path = log.split(",")[3]
                ext = path.rsplit(".")[-1]
                files = path.split("/")
                entry_cnt += 1

                if ext == "py":
                    py_cnt += 1
                elif ext == "rb":
                    rb_cnt += 1
                elif ext == "c":
                    c_cnt += 1
                elif ext == "rs":
                    rs_cnt += 1
                elif ext == "js":
                    js_cnt += 1
                elif ext == "cpp":
                    cpp_cnt += 1
                elif ext == "java":
                    java_cnt += 1
                elif ext == "class":
                    class_cnt += 1
                elif ext == "jar":
                    jar_cnt += 1
                elif ext == "pl":
                    pl_cnt += 1
                elif ext == "pm":
                    pm_cnt += 1
                elif ext == "php":
                    php_cnt += 1
                elif ext == "cgi":
                    cgi_cnt += 1
                elif ext == "txt":
                    txt_cnt += 1
                elif ext == "tex":
                    tex_cnt += 1
                elif ext == "md":
                    md_cnt += 1
                elif ext == "org":
                    org_cnt += 1
                elif any(item.startswith('.') for item in files):
                    dotfile_cnt += 1

            aggregates.append([py_cnt, rb_cnt, c_cnt, rs_cnt, js_cnt, cpp_cnt, java_cnt, class_cnt, jar_cnt, pl_cnt, pm_cnt, php_cnt, cgi_cnt, txt_cnt, tex_cnt, md_cnt, org_cnt, dotfile_cnt/25])

        return aggregates

    def cooccurrence(self, aggregates):
        co_cnt = 0

        for aggregate in aggregates:
            max = int(np.max(aggregate))
            py_val = aggregate[0]
            rb_val = aggregate[1]
            tex_val = aggregate[14]
            dot_val = aggregate[17]

            if ((max/6 < py_val) and (max/6 < dot_val)) or ((max/6 < rb_val) and (max/6 < dot_val)):
                co_cnt += 1

        return co_cnt


    def show_heatmap(self, matrix):
        transposed_matrix = [list(row) for row in zip(*matrix)]
        plt.imshow(transposed_matrix, cmap='binary', interpolation='nearest', aspect='auto')
        plt.xlabel('Number of logs')
        plt.ylabel('File type')
        plt.title('Documentation 1')
        custom_ticks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        custom_labels = ["py", "rb", "c", "rs", "js", "cpp", "java", "class", "jar", "pl", "pm", "php", "cgi", "txt", "tex", "md", "org", "dot"]
        plt.yticks(custom_ticks, custom_labels, fontsize=6)
        formatter = ticker.ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((-3, 3))
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.colorbar()
        plt.show()


def calc_cos_sim(features):
    cos_sim = []

    for feature in features:
        v1 = feature[0]
        v2 = feature[1]

        cos_sim.append(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

    return cos_sim

def calc_retio(features):
    retio = []

    for feature in features:
        f1 = feature[0]
        f2 = feature[1]

        retio.append(f1 / f2)

    return retio

def main():
    args = sys.argv
    # logfile_name_1 = args[1]
    #
    # logfile_1 = LogFile(logfile_name_1)
    # logs_1 = logfile_1.get_update()
    #
    # feature = Feature(logfile_name_1)
    # print(feature.get_feature())
    features = []
    feature = Feature()
    aggregates = []

    for file_name in args[1:]:
        # logfile = LogFile(file_name)
        # log = logfile.get_update()

        feature.set_logfile(file_name)
        features.append(feature.get_feature())
        matrix = feature.separate_by_time(5)
        aggregate = feature.aggregate_filetype(matrix)
        aggregates.append(aggregate)

    for i, aggregate in enumerate(aggregates):
        co = feature.cooccurrence(aggregate[1:])
        features[i].append(int(co))

    normalized_feature = feature.get_norm_feature(features)

    # for feature in features:
    #     print(feature)
    #
    for norm in normalized_feature:
        print([round(x, 3) for x in norm])

    kmeans = KMeans(n_clusters=3, max_iter=400, init="random", n_init="auto")
    kmeans.fit(normalized_feature)

    labels = kmeans.labels_

    print("クラスタリング結果:")
    print(labels)

if __name__ == "__main__":
    main()
