

import os
import time

def _print(string):
    print string

class FileMonitor:
    def __init__(self, file_path, communicate=False):
        if not communicate:
            self.communicate = _print
        else:
            self.communicate = communicate
        self.file_path = file_path
        #self.create_file(file_path)
        self.file_content, self.file_siz = self.read_file()
        if self.file_content:
            self.refresh_rate = 0.2
            self.stop = False
            self.mtime = os.path.getmtime(self.file_path)
            self.differ_status = False
            self.diff = []

    # def stop_thread(self):
    #     self.stop = True

    # def create_file(self, _file, overwrite=False):
    #     if not os.path.isfile(_file):
    #         self.communicate("creating file {}".format(_file))
    #         f=open(_file, 'wb')
    #         f.close()
    def refresh_file_content(self):
        self.diff = []
        self.file_content, self.file_siz = self.read_file()

    def read_file(self):
        if os.path.isfile(self.file_path):
            _file = open(self.file_path, 'r')
            file_content = _file.read()
            _file.close()
            file_siz = len(file_content)
            self.diff = []
            return file_content, file_siz
        else:
            self.communicate("File does not exist: {}".format(self.file_path))
            return None, None

    def monitor(self):
        #while not self.stop:
        mtime = os.path.getmtime(self.file_path)
        if mtime != self.mtime:
            self.mtime = mtime
            self.diff = self.get_file_diff()
        time.sleep(self.refresh_rate)

    def get_file_diff(self):
        diff = []
        file2_byte, new_siz = self.read_file()
        if new_siz == self.file_siz:
            for addr in range(0, self.file_siz):
                if self.file_content[addr] != file2_byte[addr]:
                    diff.append([addr,file2_byte[addr]])
                    #diff[addr] = new_content[addr]
            return diff
        else:
            return False
