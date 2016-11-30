#!/usr/bin/env python
import tkFileDialog, Tkinter
import options_parser
import sys
import os

class BinaryParser:
    def __init__(self, print_to_main_output = None, print_to_output2 = None):
        os.chdir(os.getcwd())
        if not print_to_main_output:
            print_to_main_output = self._print
        self.print_to_main_output = print_to_main_output
        self.print_to_output2 = print_to_output2

    def _print(self, s):
        print s

    def save_raw_data(self, data, _file):
        out = open(_file, 'wb')
        out.write(data)
        out.close()

    def read_binary_file(self, _file):
        file_b = open(_file,'rb')
        bin_ = file_b.read()
        file_b.close()
        siz = len(bin_)
        self.print_to_main_output("Binary file size: {}".format(hex(siz)))
        return bin_, siz

    def save_data_in_hex_format(self, data, _file):
        tmp = ''
        len_d = len(data)
        char_len = 16
        for d in range(0,len_d-char_len, char_len):
            _data = (' ').join([hex(ord(i)).replace('0x','').zfill(2) for i in data[d:d+char_len]])
            _str = ('').join(data[d:d+char_len].replace('\n', '0').replace('\r','0'))
            diag = "{:>6} {} {}".format(hex(d), _data, _str)
            tmp += diag + '\n'
            self.print_to_output2(diag)
        self._save_data_to_file(tmp, _file)

    def convert_bin_to_hex(self, _file):
        r = Tkinter.Tk()
        r.withdraw()
        name = tkFileDialog.askopenfilename(title='select file to convert')
        Data = open(name, 'rb')
        data = Data.read()
        Data.close()
        self.save_data_in_hex_format(data, _file)

    def compare_binaries(self, b1, b2, _file=''):
        self.print_to_main_output("Data compare with {}".format(_file))
        lb1 = len(b1)
        lb2 = len(b2)
        r = range(0, lb1)
        files_identical = True
        if lb1 > lb2:
            r = range(0, lb2)
        for i in r:
            diff = self._bin_content_compare(i, b1, b2)
            if diff:
                files_identical = False
                self.print_to_main_output('difference: {}'.format(diff))
        if files_identical:
            self.print_to_main_output("Files are binary identical")

    def _bin_content_compare(self, index, b1, b2):
        if b1[index] != b2[index]:
            d1 = hex(ord(b1[index])).replace('0x', '').zfill(2)
            d2 = hex(ord(b2[index])).replace('0x', '').zfill(2)
            i = hex(index).replace('0x', '').zfill(4)
            return "{} {} {}".format(i, d1, d2)
        return None

    def _save_data_to_file(self, data, file):
        tmp = open(file, 'w')
        tmp.write(data)
        tmp.close()

    def open_bin_file(self, path=None, dialog=None):
        if not dialog:
            dialog = 'select file'
        if not path:
            r = Tkinter.Tk()
            r.withdraw()
            path = tkFileDialog.askopenfilename(title=dialog)
            # if not path:
            #     sys.exit()
            #     self.print_to_main_output("\nOpening file:", path)
        bin_f = open(path, 'rb')
        bin_content = bin_f.read()
        bin_f.close()
        #bin_content = bin_content[0:self.eeprom_siz]
        bin_size = len(bin_content)
        self.print_to_main_output("Binary file size: %s" % (hex(bin_size)))
        return bin_content, bin_size

    def compare_two_files(self):
        file1, f1_siz = self.open_bin_file(None, "file1")
        file2, f2_siz = self.open_bin_file(None, "file2")
        self.compare_binaries(file1, file2)

    def start(self):
        options = {
            '-compare': self.compare_two_files
        }
        options_parser.options_executor(sys.argv[1:], options)

if __name__ == "__main__":
    bp = BinaryParser()
    bp.start()