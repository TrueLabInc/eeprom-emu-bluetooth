#!/usr/bin/env python
__author__ = 'rafal'

import serial
import time
import serialCommands
import os, sys
import tkFileDialog, Tkinter
import platform
#import curses
from collections import OrderedDict
from serial_list import FindUsbDevice
import thread




class Emulator:
    def __init__(self, bin_path = None):
        self.emulator_welcome = ""
        self.emulator_serial_no = "A50285BI"
        self.verbose = False
        self.platform = platform.system()
        self.linux = False
        if self.platform == 'Linux':
            self.linux = True
            self.digitool_serial_port = "//dev//ttyUSB0"
            self.clear_command = "clear"
        # elif self.platform == 'Windows':
        #     self.digitool_serial_port = self.find_digi_tool_in_com_devices(verbose=False)
        #     self.clear_command = "cls"
        self.emulator_config_name = 'emulator.conf'
        self.path = bin_path
        self.rx_buffer_size = 64
        self.emulator_serial = None
        try:
            self.emualtor_baud_rate = int(self.read_config_file()['baud'])
        except:
            self.store_baud_rate('250000')
            self.emualtor_baud_rate = int(self.read_config_file()['baud'])
        if not self.try_call_emulator(self.emualtor_baud_rate):
            self.emualtor_baud_rate = self.detect_baud()
            self.store_baud_rate(self.emualtor_baud_rate)
        self.emulator_serial = None
        os.system(self.clear_command)
        self.welcome()
        self.options = {
            '-f': self.find_emulator_in_com_devices,
            '-v': self.set_verbose,
        }

    def set_verbose(self):
        self.verbose = True

    def input_thread(self, list):
        raw_input()
        list.append(None)

    def clear_screen(self):
        os.system(self.clear_command)

    def open_bin_file(self):
        if not self.path:
            r = Tkinter.Tk()
            r.withdraw()
            self.path = tkFileDialog.askopenfilename(title='select file to write')
            if not self.path:
                sys.exit()
        print "\nOpening binary file:", self.path
        bin_f = open(self.path, 'rb')
        bin_content = bin_f.read()
        bin_f.close()
        bin_content = bin_content[0:0x8000]
        bin_size = len(bin_content)
        print "Binary file size: %s"    %   (hex(bin_size))
        return bin_content, bin_size

    def open_serial_port(self):
        if not self.emulator_serial:
            print "\nOpening serial connection"
            try:
                #self.digi_tool_serial = serial.Serial(port=self.digitool_serial_port, baudrate=self.digitool_baud_rate, parity=serial.PARITY_EVEN)
                self.emulator_serial = serial.Serial(port=self.digitool_serial_port, baudrate=self.emualtor_baud_rate)
            except:
                print "Could not open serial connection with digi tool"
                print
        return self.emulator_serial

    def open_serial_port_with_negotiation(self, baud):
        print "\nOpening serial connection with baud", baud
        self.emulator_serial = serial.Serial(port=self.digitool_serial_port, baudrate=baud, timeout=0.2)
        return self.emulator_serial

    def close_serial_port(self):
        self.emulator_serial.close()


    def wait_for_digitool(self):
        sc = serialCommands.serial_commands_rx
        sc_err = serialCommands.serial_commands_rx_errors
        conn = self.emulator_serial
        rcv_byte = 0
        while rcv_byte != sc["digiToolRxBufferReady"]:
            rcv_byte = ord(conn.read())
            if rcv_byte in sc_err:
                return rcv_byte
            elif rcv_byte == sc["digiToolRxBufferReady"]:
                break
            #print rcv_byte
            #time.sleep(0.00001)

            #time.sleep(0.1)

    def wait_for_digidata(self):
        sc = serialCommands.serial_commands_rx
        conn = self.emulator_serial
        rcv_bin = 0
        self.verbose("wait for data")
        while rcv_bin != sc["sendingData"]:
            rcv_bin = ord(conn.read())
            time.sleep(0.0001)

    def test(self):
        self.open_serial_port()
        "serial connection ready"
        self.wait_for_digitool()


    def read_eeprom(self, conn):
        rcv_bin = ''
        read_eeprom_command = serialCommands.serial_commands_tx['read_eeprom']
        conn.write(read_eeprom_command)
        while not conn.inWaiting():
            conn.flushOutput()
            conn.write(read_eeprom_command)
            time.sleep(0.5)
            print ".",
        self.wait_for_digidata()
        ln = len(rcv_bin)
        print "\nReading eeprom file"
        while ln != 32768:
            rcv_bin += conn.read()
            ln = len(rcv_bin)
            if not ln%100:
                self.progress_bar(ln, 32768)
        print
        print "reading done"
        print
        return rcv_bin

    def progress_bar(self, val, maxi):
        bar_len = 50
        print bar_len*'\b' + int(float(val)/maxi*bar_len)*"#" + int((float(maxi-val)/maxi*bar_len))*".",

    def verify_binary_file(self, bin_file, conn, t0):
        print "\nBinary files verifiaction"
        self.verbose("wait for digitool")
        self.wait_for_digitool()
        tim0 = time.time()
        rcv_bin = self.read_eeprom(conn)
        print "read time:", time.time() - tim0
        self.compare_files(bin_file, rcv_bin, t0)

    def welcome(self):
        msg = "" \
              "\n" \
              "EEPROM Emulator\n" \
              "Version: 0\n\n" \
              "Emulator uC version:\n" \
              "{}".format(self.emulator_welcome.split('\n')[1])

        print msg

    def find_emulator_in_com_devices(self):
        port_found = None
        print
        if self.verbose:
            print "All vailable com devices"
            FindUsbDevice(self.platform).print_devices_info()
        devs = FindUsbDevice(self.platform).get_devices_info()
        for d in devs:
            device = devs[d]
            if device['serial_number'] == self.emulator_serial_no:
                port_found = device['device']
        if not port_found:
            print
            print "!!! Unable to find Emulator in serial ports !!!\n"
            time.sleep(2)
            sys.exit()
        elif self.verbose:
            print
            print "Emulator found at {}\n".format(port_found)
            raw_input("\nENTER to close")
        return port_found

    def remove_bad_characters(self, line):
        bad_chars = [' ', '\n']
        for c in bad_chars:
            line.replace(c, '')
        return line

    def check_for_config_file(self):
        try:
            conf_file = open(self.emulator_config_name, 'r')
        except:
            print "Creating config file"
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

            if ':' in line:
                entry = self.remove_bad_characters(line).split(':')
                config_entries[entry[0]] = entry[1]
        return config_entries

    def save_config_file(self, config_entries):
        conf_file = open(self.emulator_config_name, 'w')
        conf_file.writelines('DIGITOOL CONFIGURATION\n')
        for k in config_entries:
            line = "{}: {}\n".format(k,config_entries[k])
            conf_file.write(line)
        conf_file.close()

    def detect_baud(self,):
        bauds_to_try = [9600, 14400, 19200, 28800, 38400, 57600,  115200, 250000, 500000]
        for b in bauds_to_try:
            if self.try_call_emulator(b):
                print "Detected baud:", b
                return b
        print "Can't connect with emulator with tried baud rates"

    def try_call_emulator(self, b):
        handshake_str = "***EEPROM emulator***"
        emulator = self.open_serial_port_with_negotiation(b)
        if emulator.isOpen():
            timeout = 1
            handshake = serialCommands.serial_commands_tx['call']
            read = ''
            ldt = len(handshake_str)
            start_t = time.time()
            while not handshake_str in read:
                if self.platform == "Linux":
                    outwaiting = emulator.out_waiting
                elif self.platform == "Windows":
                    outwaiting = emulator.outWaiting()
                if outwaiting:
                    emulator.flushOutput()
                emulator.write(handshake)
                while emulator.inWaiting()<ldt:
                    current_time = time.time()
                    if current_time - start_t > timeout:
                        break
                    time.sleep(0.01)
                read = emulator.read(emulator.inWaiting())
                print read
                current_time = time.time()
                if current_time - start_t > timeout:
                    emulator.close()
                    print "try failed"
                    return False
            emulator.close()
            self.emulator_welcome = read
            return True
        return False

    def store_baud_rate(self, baudrate):
        self.check_for_config_file()
        config_entries = self.read_config_file()
        config_entries['baud'] = baudrate
        self.save_config_file(config_entries)

    def listen_for_digitool(self):
        conn = self.open_serial_port()
        cnt = 0
        list = []
        out=''
        thread.start_new_thread(self.input_thread, (list,))
        while not list:
            while not conn.inWaiting():
                time.sleep(0.00001)
            data = conn.read()
            data = hex(ord(data))
            out += '{:5}'.format(data)
            cnt += 1
            if cnt > 100:
                self.clear_screen()
                print out
                out = ''
                cnt = 0
            if not cnt % 10:
                out += '\n'

    def catch_avr_load(self, conn):
        timeout = 0.5
        amount_of_bytes = 7
        free_ram_h_ind = 5
        free_ram_l_ind = 4
        ram_h_ind = 3
        ram_l_ind = 2
        cpu_h_ind = 1
        cpu_l_ind = 0
        avr_load = None
        sc = serialCommands.serial_commands_rx
        conn.write(serialCommands.serial_commands_tx['cpu_load'])
        t1 = time.time()
        char = ord(conn.read(1))
        while char!=sc["cpuLoad"]:
            time.sleep(0.0001)
            if time.time()-t1>timeout:
                break
            char = ord(conn.read(1))
        if char==sc["cpuLoad"]:
            #print "got char"
            #rcv_bin = conn.readall()
            #print len(rcv_bin)
            while conn.in_waiting != amount_of_bytes:
                time.sleep(0.0001)
                if time.time()-t1>timeout:
                    #print "break"
                    break
                rcv_bin = conn.read(amount_of_bytes)
                #rcv_bin = conn.readall()
                #print len(rcv_bin)
                if(ord(rcv_bin[-1])==sc["cpuLoad"]):
                    rcv_bin = rcv_bin[0:-1]
                    cpu_load = 0xff*ord(rcv_bin[cpu_h_ind]) + ord(rcv_bin[cpu_l_ind])
                    free_mem = 0xff*ord(rcv_bin[ram_h_ind]) + ord(rcv_bin[ram_l_ind])
                    min_free_mem = 0xff * ord(rcv_bin[free_ram_h_ind]) + ord(rcv_bin[free_ram_l_ind])
                    avr_load = (cpu_load, free_mem, min_free_mem)
        return avr_load

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

    def options_parser(self, args):
        options = OrderedDict()
        l = len(args)
        for i,a in enumerate(args):
            option = None
            if '-' in a:
                option = a
                options[option] = None
            if option and i+1<=(l-1):
                n = args[i+1]
                if not '-' in n:
                    options[option] = n
        return options

    def start(self):
        args = sys.argv[1:]
        options = self.options_parser(args)
        execution_list = []
        for o in options:
            if o in self.options:
                execution_list.append(o)
            else:
                print "{} option not supperted".format(o)
        try:
            execution_list.pop(execution_list.index('-v'))
            execution_list.insert(0, '-v')
        except:
            pass
        for e in execution_list:
            self.options[e]()



if __name__ == "__main__":
    Emulator().start()
    #DigiTool("1.bin").detect_baud()

