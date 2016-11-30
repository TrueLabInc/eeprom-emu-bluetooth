#!/usr/bin/env python
__author__ = 'rafal'

import random
import time
from serialCommands import Commands
import os, sys
import tkFileDialog, Tkinter
import platform
#import curses
#from collections import OrderedDict
from serial_list import FindUsbDevice
import subprocess
import thread
import bluetooth
import numpy as np
import options_parser
from binary_parser import BinaryParser

class PrintOutputStruct:
    def __init__(self, siz=30):
        self.structure = {
            'content':siz*[''],
            'cursor':0,
            'size':siz
        }

class Emulator:
    # """
    # pybluez installation:
    # sudo apt-get update
    # sudo apt-get install python-pip python-dev ipython
    # sudo apt-get install bluetooth libbluetooth-dev
    # sudo pip install pybluez
    #
    # "hcitool scan" to find bt address
    # """
    def __init__(self, bin_path = None):
        self.binary_parser = BinaryParser(self.print_to_main_output, self.print_to_console1)
        self.eeprom_siz = 0x8000
        self.threads_running = True
        self.cmds = Commands()
        self.main_output = PrintOutputStruct(siz=30).structure
        self.console1 = PrintOutputStruct(siz=15).structure
        self.verbose = False
        self.platform = platform.system()
        self.linux = False
        if self.platform == 'Linux':
            self.linux = True
            self.clear_screen = "clear"
        elif self.platform == 'Windows':
             self.clear_screen = "cls"
        self.emulator_config_name = '/home/rafal/eeprom-emu-bluetooth/emulator.conf'
        self.path = bin_path
        self.emulator_rx_buffer_size = 64
        self.emulator_bt_port = None
        try:
            self.emulator_bt_address = self.read_config_file()['address']
            self.emulator_bt_port = self.read_config_file()['port']
        except:
            self.store_bt_config('address','00:11:35:91:36:65')
            self.store_bt_config('port', '1')
            self.emulator_bt_address = self.read_config_file()['address']
            self.emualtor_bt_port = self.read_config_file()['port']
        self.emulator = self.call_emulator(self.emulator_bt_address, self.emulator_bt_port)
        if self.emulator:
            #self.emulator_welcome = self.emu_receive()
            #self.welcome()
            os.system(self.clear_screen)
            self.rcv_console1_buff = ''
            self.rcv_buff = ''
            #self.start_listener()
            thread.start_new_thread(self.print_thread, (0.4,))
            #self.emu_send_n(self.cmds.tx.call)

            self.options = {
                '-w': self.send_eeprom_file,
                '-r': self.read_sram,
                '-F': self.read_flash,
                '-c': self.handshake,
                '-f': self.find_emulator_in_rfcom_devices,
                '-v': self.set_verbose,
                '-l': self.start_listener,
                '-C': self.binary_parser.convert_bin_to_hex
            }
            self.start()
            self.print_output()
            #self.start_while()
        else:
            msg = "\n" \
                  "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" \
                  "Could not connect to bluetooth device\n" \
                  "Is device {} busy ?\n" \
                  "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".format(self.emulator_bt_address)
            rfcom_status = subprocess.Popen('rfcomm', stdout=subprocess.PIPE)
            out, err = rfcom_status.communicate()
            print msg
            if (self.emulator_bt_address in out) and ('connected' in out):
                print "--->{}".format(out)
                print "Yes it is busy !"
        self.threads_running = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.emulator:
            self.emulator.close()

    def handshake(self):
        self.emu_send_n('c')

    def start_while(self):
        while 1:
            self.print_output()
            time.sleep(0.1)
            # if self.rcv_buff:
            #     self.print_to_console1(self.rcv_buff)
            #     self.rcv_buff = ''

    def wait_for_msg(self, msg, timeout=1):
        ret_msg = ''
        t0 = time.time()
        #buff = ''.join(self.console1)
        buff = self.rcv_buff
        while not (msg in buff):
            time.sleep(0.01)
            t1 = time.time()
            if t1 - t0 > timeout:
                break
            buff = self.rcv_buff
        if msg in buff:
            f = buff.find(msg)
            ret_msg = buff[0:f]
        #self.rcv_buff = ''
        return ret_msg


    def start_listener(self):
        t0 = time.time()
        self.listener_thread = thread.start_new_thread(self.listen_for_emu, (t0,))

    def reset_avr(self):
        self.emulator.send(self.cmds.tx.reset + '\n')
        time.sleep(0.5)

    def b_zfill(self, v):
        v = bin(ord(v))[2:]
        v = v[::-1]
        return v + (8-len(v))*'0'

    def initilize_write_process(self):
        #self.reset_avr()
        self.emulator.send(self.cmds.tx.write_to_flash+'\n')
        self.wait_for_string_2('test')

    def initilize_read_sram_process(self):
        self.emulator.send(self.cmds.tx.read_sram+'\n')
        self.wait_for_string_2('sending')

    def initilize_read_flash_process(self):
        self.emulator.send(self.cmds.tx.read_flash+'\n')
        self.wait_for_string_2('sending')

    def send_eeprom_file(self, _file):
        bin_, num_of_bytes = self.binary_parser.read_binary_file(_file)
        self.print_to_main_output("Transmitting file")
        self.initilize_write_process()
        buff_siz = 1024
        t0 = time.time()
        errors = [1,2,3,4,9,55]
        tmp_cnt = 0
        self.print_to_main_output("Progress:")
        for k in range(0, num_of_bytes, buff_siz):
            self.print_to_main_output(self.progress_bar(k,num_of_bytes), scroll=False)
            page = bin_[k:k+buff_siz]
            crc = self.crc(page)
            #if tmp_cnt in errors:
            #    page = self.corrupt_packet_for_test(page)
            crc_s = "".join([chr(crc&0xff), chr(crc>>8)])
            self.emulator.send(page+crc_s)
            while self.emulator.recv(1) != '.':
                pass
            tmp_cnt += 1
        self.verify_crc_with_feedback(bin_, buff_siz)
        self.print_to_main_output("Elapsed time {}".format(time.time() - t0))

    def _receive_data(self):
        data = ''
        len_d = 0
        while len_d < self.eeprom_siz:
            try:
                data += self.emulator.recv(20)
            except:
                return data
            len_d = len(data)
        return data

    # def _save_data_in_hex_format(self, data, _file):
    #     tmp = ''
    #     len_d = len(data)
    #     char_len = 16
    #     for d in range(0,len_d-char_len, char_len):
    #         _data = (' ').join([hex(ord(i)).replace('0x','').zfill(2) for i in data[d:d+char_len]])
    #         _str = ('').join(data[d:d+char_len].replace('\n', '0').replace('\r','0'))
    #         diag = "{:>6} {} {}".format(hex(d), _data, _str)
    #         tmp += diag + '\n'
    #         self.print_to_console1(diag)
    #     self._save_data_to_file(tmp, _file)

    def _receive_and_process_data(self, _file):
        data = self._receive_data()
        if '.bin' in _file:
            bin, b_siz = self.binary_parser.open_bin_file(_file)
            self.binary_parser.compare_binaries(data, bin, _file)
        else:
            self.binary_parser.save_data_in_hex_format(data, _file)
            _file = _file.split('.')[0] + '.bin'
            self.binary_parser.save_raw_data(data, _file)
        self.print_to_main_output("Receive data done")

    def read_flash(self, _file):
        self.print_to_main_output("Reading flash content")
        self.initilize_read_flash_process()
        self._receive_and_process_data()

    def read_sram(self, _file):
        self.print_to_main_output("Reading sram content")
        self.initilize_read_sram_process()
        self._receive_and_process_data(_file)

    def verify_crc_with_feedback(self, bin_, buff_siz):
        result = self.wait_for_str_len(3)
        if result == 'nok':
            self.print_to_main_output("CRC problems")
            while True:
                result = self.wait_for_str_len(3)
                if 'ack' in result:
                    self.print_to_main_output(result)
                    return True
                if result[1] != '\0':
                    self.print_to_main_output("Retransmission failed!")
                    return False
                page_num = ord(result[0])
                self.print_to_main_output("Resending page: {}".format(page_num))
                page = bin_[page_num*buff_siz:(page_num+1)*buff_siz]
                crc = self.crc(page)
                crc_s = "".join([chr(crc & 0xff), chr(crc >> 8)])
                self.emulator.send(page + crc_s)
        if result == 'ack':
            self.print_to_main_output("CRC verification OK")
            return True
        else:
            self.print_to_main_output("Unexpected response !: {}".format(result))
            return False

    def corrupt_packet_for_test(self, l):
        n = random.randint(0,255)
        c = l[n]
        e = chr(random.randint(0,255))
        while e==c:
            e = chr(random.randint(0, 255))
        return l[:n] + e + l[n+1:]

    def wait_for_str_len(self, length, timeout=3):
        data = ''
        t0 = time.time()
        while len(data) < length:
            data += self.emulator.recv(length)
            time.sleep(0.001)
            if time.time() - t0 > timeout:
                return False
        return data

    def wait_for_str(self, string):
        data = self.emulator.recv(10)
        while not (string in data):
            time.sleep(0.001)
            data = self.emulator.recv(10)
        print data

    def wait_for_string_2(self, string, timeout=5):
        t0 = time.time()
        data = "0"
        buff = ""
        while not (string in data):
            data = self.emulator.recv(20)
            buff += data
            if time.time() - t0 > timeout:
                print "Timeout {}".format(timeout)
                break
            time.sleep(0.01)
        return buff

    def wait_for_crc(self, crc_len = 1):
        data = self.emulator.recv(crc_len)
        while len(data)<crc_len:
            data += self.emulator.recv(crc_len)
            time.sleep(0.0001)
        return data

    def crc_xmodem(self, crc, data):
        crc = np.uint16(crc ^ (data << 8))
        for i in range(0, 8):
            if crc & 0x8000:
                crc = np.uint16((crc << 1) ^ 0x1021)
            else:
                crc = np.uint16(crc << 1)
        return crc

    def crc(self, buffer):
        crc = 0
        for i in buffer:
            crc = self.crc_xmodem(crc, ord(i))
        return crc

    def print_output(self):
        main_output_len = self.main_output['size']
        console1_len = self.console1['size']
        main_output = self.main_output['content'][0:main_output_len]
        console1 = self.console1['content'][0:console1_len]
        os.system(self.clear_screen)
        for l in main_output:
            print l
        print (main_output_len - len(main_output))*'\n'
        print "{}console1{}".format(30*'*',30*'*')
        for l in console1:
            print l
        print (console1_len -len(console1))*'\n'
        #self.main_ouput = ''
        #self.console1 = ''

    def print_to_console1(self, string, scroll=True):
        self._print_to(self.console1, string, scroll)
        #self.console1 = self.add_at_list_bottom(self.console1, string)

    def print_to_main_output(self, string, scroll=True):
        self._print_to(self.main_output, string, scroll)
        #self.main_ouput = self.add_at_list_bottom(self.main_ouput, string, scroll)

    def _print_to(self, object, string, scroll=False):
        content = object['content']
        cursor = object['cursor']
        siz = object['size']-1
        if scroll:
            if cursor<siz:
                cursor+=1
                object['content'][cursor] = string
                object['cursor'] = cursor
            elif cursor==siz:
                object['content'][0:-1] = content[1:]
                object['content'][cursor] = string
        if scroll==False:
            if cursor<siz:
                object['content'][cursor+1] = string
            else:
                object['content'][0:-1] = content[0:-1]
                object['content'][cursor] = string
        #object['content'][cursor] = string

    def add_at_list_top(self, l = ['.'], v = '.'):
        l[1:] = l[0:-1]
        l[0] = v
        return l

    def add_at_list_bottom(self, string_list = ['.'], string ='.', scroll=True):
        try:
            idx = string_list.index('')
        except:
            idx = len(string_list) - 1
            string_list = string_list[1:] + ['']
        tmp_l = string_list[0:idx]
        tmp_l.append(string)
        tmp_l += string_list[idx + 1:]
        if scroll==False:
            tmp_l[idx] = string
        return tmp_l

    def find_emulator_in_rfcom_devices(self):
        pass

    def emu_send_with_ack(self, data):
        data += self.cmds.tx.ack + '\n'
        self.emulator.send(data)
        #self.emulator.send('\n')

    def emu_send_n(self, string):
        string += '\n'
        self.emulator.send(string)

    def print_thread(self, referesh_period=0.2):
        while self.threads_running:
            self.print_output()
            time.sleep(referesh_period)

    def listen_for_emu(self, t0):
        cnt = 0
        timeout = 0.25
        while 1:
            self.print_output()
            time.sleep(0.01)
            try:
                rcv = self.emulator.recv(256)
                # self.rcv_console1_buff = rcv
                self.rcv_buff += rcv
                self.print_to_console1(rcv)
                if len(self.rcv_buff >512):
                    self.rcv_buff  = ''
            except:
                pass
            # if 'timeout' in self.rcv_buff:
            #     self.print_to_main_output("closing thread")
            #     self.listener_thread.exit_thread()
            # if time.time() - t0 > timeout:
            #     t0 = time.time()
            #     self.emu_send('u')


    def emu_receive(self,buffer=10):
        timeout = 3
        rcv = ''
        t0 = time.time()
        while not 'end' in rcv:
            rcv += self.emulator.recv(buffer)
            time.sleep(0.001)
            if time.time() - t0 > timeout:
                self.print_to_main_output("timeout")
                break
        return rcv

    def call_emulator(self, address, port, num_of_tries = 5):
        msg = "Connecting to bt device addr: {}, port: {}".format(address, port)
        print msg
        self.print_to_main_output(msg)
        try_num = 0
        self.emu_timeout = 2
        while try_num <= num_of_tries:
            try:
                emu = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                emu.connect((address, int(port)))
                emu.settimeout(self.emu_timeout)
                print "connected"
                return emu
            except:
                try_num += 1
                print "Connection fail. Try: {}".format(try_num)

    def set_verbose(self):
        self.verbose = True

    def input_thread(self, list):
        raw_input()
        list.append(None)

    def clear_screen(self):
        os.system(self.clear_screen)

    # def open_bin_file(self, path=None):
    #     if not path:
    #         r = Tkinter.Tk()
    #         r.withdraw()
    #         path = tkFileDialog.askopenfilename(title='select file to write')
    #         if not path:
    #             sys.exit()
    #             self.print_to_main_output("\nOpening binary file:", path)
    #     bin_f = open(path, 'rb')
    #     bin_content = bin_f.read()
    #     bin_f.close()
    #     bin_content = bin_content[0:self.eeprom_siz]
    #     bin_size = len(bin_content)
    #     self.print_to_main_output("Binary file size: %s" % (hex(bin_size)))
    #     return bin_content, bin_size

    def progress_bar(self, val, maxi):
        bar_len = 50
        #return bar_len*'\b' + int(float(val)/maxi*bar_len)*"#" + int((float(maxi-val)/maxi*bar_len))*".",
        return int(float(val) / maxi * bar_len) * "#" + int((float(maxi - val) / maxi * bar_len)) * "."

    def welcome(self):
        #msg = self.emulator_welcome.split('\n')
        msg = "" \
              "\n" \
              "EEPROM Emulator\n" \
              "Version: 0\n\n" \
              "Emulator uC version:\n" \
              "{} {}".format(msg[1], msg[3])
        self.print_to_main_output(msg)
        print(msg)

    def remove_bad_characters(self, line):
        bad_chars = [' ', '\n', '\r']
        for c in bad_chars:
            while c in line:
                line = line.replace(c, '')
        return line

    def check_for_config_file(self):
        try:
            conf_file = open(self.emulator_config_name, 'r')
        except:
            self.print_to_main_output("Creating config file")
            conf_file = open(self.emulator_config_name, 'w')
            conf_file.writelines('EMULATOR CONFIGURATION\n')
            conf_file.close()
            conf_file = open(self.emulator_config_name, 'r')
        return conf_file

    def read_config_file(self):
        conf_file = self.check_for_config_file()
        config_entries = {}
        config = conf_file.readlines()
        conf_file.close()
        for line in config:
            if '-' in line:
                entry = self.remove_bad_characters(line).split('-')
                config_entries[entry[0]] = entry[1]
        return config_entries

    def save_config_file(self, config_entries):
        conf_file = open(self.emulator_config_name, 'w')
        conf_file.writelines('EMULATOR CONFIGURATION\n')
        for k in config_entries:
            line = "{}- {}\n".format(k,config_entries[k])
            conf_file.write(line)
        conf_file.close()

    def store_bt_config(self, entry, value):
        config_entries = self.read_config_file()
        config_entries[entry] = value
        self.save_config_file(config_entries)

    def create_bar(self, val, label, max=2000, len=50):
        if val > max:
            val = max
        V = str(val)
        bar = label
        val = len*val/max
        if val > len:
            val = len-1
        bar+=val*'#'+'.'*(len-val)+V
        return bar

    def restore_terminal_behaviour(self):
        os.system('reset')

    def start(self):
        args = sys.argv[1:]
        options_parser.options_executor(args, self.options, output = self.print_to_main_output)




if __name__ == "__main__":
    Emulator()
    #DigiTool("1.bin").detect_baud()

