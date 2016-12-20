
import bluetooth
from config_file import ConfigFileParser
import os
import time
from serial_commands import TX_commands
from binary_parser import BinaryParser
import crc
import popup_window
#from PyQt4.QtGui import QMessageBox

class Emulator_2():
    def __init__(self, communicate, progress_signal):
        self.conn = None
        self.progress_signal = progress_signal
        self.eeprom_siz = 0x8000
        self.TX_commands = TX_commands()
        self.communicate = communicate
        self.binary_parser = BinaryParser(self.communicate, self.communicate)
        self.emulator_config_name = '/'.join([os.getcwd(), "emulator.conf"])
        self.cfg_file = ConfigFileParser(self.emulator_config_name, communicate, config_header="EMULATOR CONFIGURATION")
        self.load_config_file()
        self.ping_rcv = ''

        #self.connection = self.call_emulator(self.emulator_bt_address, self.emulator_bt_port)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.emulator:
            self.emulator.close()

    def load_config_file(self):
        try:
            self.emulator_bt_address = self.cfg_file.read_config_file()['address']
            self.emulator_bt_port = self.cfg_file.read_config_file()['port']
            self.flash_bank_in_use = self.cfg_file.read_config_file()['flash_bank']
        except:
            self.cfg_file.store_bt_config('address', '00:11:35:91:36:65')
            self.cfg_file.store_bt_config('port', '1')
            self.cfg_file.store_bt_config('flash_bank', '1');
            self.emulator_bt_address = self.cfg_file.read_config_file()['address']
            self.emualtor_bt_port = self.cfg_file.read_config_file()['port']
        self.emulator_bt_address = self.cfg_file.read_config_file()['address']
        self.emulator_bt_port = self.cfg_file.read_config_file()['port']
        self.flash_bank_in_use = self.cfg_file.read_config_file()['flash_bank']

    def call_emulator(self, num_of_tries = 3):
        #self.progress_signal(40)
        msg = "Connecting to bt device addr: {}, port: {}".format(self.emulator_bt_address, self.emulator_bt_port)
        self.communicate(msg)
        try_num = 0
        self.emu_timeout = 2
        while try_num <= num_of_tries:
            try:
                emu = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                emu.connect((self.emulator_bt_address, int(self.emulator_bt_port)))
                emu.settimeout(self.emu_timeout)
                self.communicate("connected")
                self._emulator = emu
                return emu
            except:
                try_num += 1
                self.communicate("Connection fail. Try: {}".format(try_num))
        self.communicate("Could not connect")

    def ping_emulator(self, diode=None, display=False):
        timeout = 2
        t0 = time.time()
        r=''
        if display:
            self.communicate("Ping device")
        self._emulator.settimeout(0.01)
        while (not 'p' in r):
            self._emulator.send('p\n')
            time.sleep(0.01)
            try:
                r+=self._emulator.recv(1)
                if 'p' in r:
                    break
            except:
                pass
            if time.time() - t0 > timeout:
                self.communicate("timeout")
                self.communicate(r)
                self._emulator.settimeout(self.emu_timeout)
                if diode:
                    diode.blink(0.2, "nok")
                return
        if diode:
            diode.blink(0.2)
        self._emulator.settimeout(self.emu_timeout)
        if display:
            self.communicate("ping: {:2.5f}s\n".format(time.time() - t0))

    def set_flash_bank(self, bank):
        self.ping_emulator()
        if bank==1:
            self._emulator.send(self.TX_commands.bank1 + '\n')
            return self._wait_for_bank_change_indication(self.TX_commands.bank1)
        elif bank==2:
            self._emulator.send(self.TX_commands.bank2 + '\n')
            return self._wait_for_bank_change_indication(self.TX_commands.bank2)
        elif bank==3:
            self._emulator.send(self.TX_commands.bank3 + '\n')
            return self._wait_for_bank_change_indication(self.TX_commands.bank3)

    def _wait_for_bank_change_indication(self, bank):
        if bank in self.wait_for_str(bank):
            self.communicate("bank changed to: {}".format(bank))
            return True
        else:
            self.communicate("bank change failed!")
            return False

    def get_flash_stats(self):
        self.ping_emulator()
        time.sleep(0.2)
        self._emulator.send(self.TX_commands.get_flash_stats + '\n')
        stats = self.wait_for_string("end")
        if "end" in stats:
            stats = stats.replace("end",'')
        if 'p' in stats:
            stats = stats.replace("p",'')
        stats = stats.split('\n')
        stats = [int(i) for i in stats if i.isdigit()]
        summary = {
            'bankInUse': stats[0],
            'flashWear1': stats[1],
            'flashWear2': stats[2],
            'flashWear3': stats[3],
        }
        return summary

    def read_sram(self, _file, diode=None):
        self.initilize_read_sram_process()
        self.communicate("Reading sram content")
        _file = self._receive_and_process_data(_file, diode)
        return _file

    def initilize_read_sram_process(self):
        self.ping_emulator(None)
        #time.sleep(0.5)
        self._emulator.send(self.TX_commands.read_sram+'\n')
        self.wait_for_string('sending')

    def initilize_read_flash_process(self):
        self.ping_emulator(None)
        #time.sleep(0.5)
        self._emulator.send(self.TX_commands.read_flash+'\n')
        self.wait_for_string('sending')

    def read_flash(self, _file, diode=None):
        self.initilize_read_flash_process()
        self.communicate("Reading flash content")
        _file = self._receive_and_process_data(_file, diode)
        return _file

    def keep_emulator_awaken(self):
        self.ping_emulator()
        self._emulator.send(self.TX_commands.keep_awake+'\n')
        self.wait_for_str('emu_on')

    def let_emulator_sleep(self):
        self.ping_emulator()
        self._emulator.send(self.TX_commands.let_sleep+'\n')
        self.wait_for_str('emu_off')

    def emulate(self, file_monitor, indicator):
        file_monitor.monitor()
        if file_monitor.diff:
            indicator(1)
            self.communicate("emulating")
            diff = file_monitor.diff
            file_monitor.refresh_file_content()
            self.update_emulated_file(diff)
            indicator(0)

    def update_emulated_file(self, diff):
        len_diff = len(diff)
        emu_buff_siz = 256
        self.communicate("Updating emulated file wiht {} bytes".format(len(diff)))
        for i in range(0, len_diff, emu_buff_siz):
            if i + emu_buff_siz < len_diff:
                d = diff[i:i + emu_buff_siz]
            else:
                d = diff[i:]
            self.send_set_of_bytes(d)
            self.progress_signal((100 * (i+1)) / len_diff)
        self.progress_signal(100)
        self.communicate("done")
        self.communicate("")
        self.communicate("EEPROM image updated to SRAM")
        self.communicate("Changes are valid until EMULATED device power down")
        self.communicate("To save changes permanently select bank and press UPLOAD")
        self.communicate("...this stores data to permanent flash")
        self.communicate("")

    def send_set_of_bytes(self, addr_byte_list):
        """

        :param addr_byte_list: dictionary of {addr, byte}
        :return:
        """
        #self.ping_emulator()
        self._emulator.send(self.TX_commands.write_single_byte+'\n')
        self.wait_for_str('>')
        amount = self.uint16_to_chars(len(addr_byte_list))
        self._emulator.send(amount)
        addr_idx = 0
        byte_idx = 1
        for a in addr_byte_list:
            self.send_single_addr_byte(a[addr_idx], a[byte_idx])

    def wait_for_str(self, string, timeout=3, raise_exception=False):
        t0 = time.time()
        num_of_chars = len(string)
        data = self._emulator.recv(num_of_chars)
        while not (string in data):
            try:
                data = self._emulator.recv(num_of_chars)
            except:
                msg = "timeout waiting for {}. Received: {}".format(string, data)
                if time.time()-t0> timeout and raise_exception:
                    raise Exception(msg)
                else:
                    self.communicate(msg)
                    break
            time.sleep(0.0001)
        return data

    def send_single_addr_byte(self, addr, byte):
        """

        :param address: two char uint16_t value
        :param byte: single char uint8_t value
        :return:
        """
        #self.communicate("{} {}".format(ord(byte), hex(addr)))
        address = chr(addr % 256) + chr((addr) / 256)
        self._emulator.send(byte+address)

    def uint16_to_chars(self, val):
        import struct
        out = chr((val) / 256) + chr(val % 256)
        return out
        #return struct.pack('H', val)

    def write_flash(self, _file):
        _bin, num_of_bytes = self.binary_parser.read_binary_file(_file)
        if num_of_bytes == self.eeprom_siz:
            self.communicate("Transmitting file")
            self.initilize_write_process()
            buff_siz = 1024*2
            t0 = time.time()
            tmp_cnt = 0
            for k in range(0, num_of_bytes, buff_siz):
                page = _bin[k:k+buff_siz]
                _crc = crc.crc(page)
                self._emulator.send(page+_crc)
                try:
                    while self._emulator.recv(1) != '.':
                        pass
                except:
                    popup_window.warning_box("Something went wrong.\n"
                                             "Operation cancelled", "!!!")
                    return
                tmp_cnt += 1
                self.progress_signal(100 * (k + buff_siz) / num_of_bytes)
            self.verify_crc_with_feedback(_bin, buff_siz)
            self.communicate("Elapsed time {}".format(time.time() - t0))
        else:
            msg = "File size is wrong. \n" \
                  "Not 27256 EEPROM image !"
            detailed_message = "File size: {} bytes\n" \
                               "expected size: {} bytes".format(num_of_bytes, self.eeprom_siz)
            self.communicate(msg)
            popup_window.warning_box(msg, detailed_msg= detailed_message, title="Operation cancelled!")
            # mbox = QMessageBox()
            # mbox.setIcon(QMessageBox.Warning)
            # mbox.setText(msg)
            # mbox.setStandardButtons(QMessageBox.Ok)
            # mbox.setDetailedText()
            # mbox.setWindowTitle("Operation canceled")
            # mbox.exec_()


    def wait_for_str_len(self, length, timeout=3):
        data = ''
        t0 = time.time()
        while len(data) < length:
            data += self._emulator.recv(length)
            time.sleep(0.001)
            if time.time() - t0 > timeout:
                return False
        return data

    def verify_crc_with_feedback(self, bin_, buff_siz):
        result = self.wait_for_str_len(1)
        nok = 'n'
        ack = 'a'
        if result == nok:
            self.communicate("CRC problems")
            while True:
                result = self.wait_for_str_len(3)
                if ack in result:
                    self.communicate(result)
                    return True
                if result[1] != '\0':
                    self.communicate("Retransmission failed!")
                    return False
                page_num = ord(result[0])
                self.communicate("Resending page: {}".format(page_num))
                page = bin_[page_num*buff_siz:(page_num+1)*buff_siz]
                crc = self.crc(page)
                crc_s = "".join([chr(crc & 0xff), chr(crc >> 8)])
                self._emulator.send(page + crc_s)
        if result == ack:
            self.communicate("CRC verification OK")
            self.communicate(" ")
            self.communicate("EEPROM image pemamently stored to selected bank")
            self.communicate(" ")
            return True
        else:
            self.communicate("Unexpected response !: '{}'".format(result))
            return False

    def initilize_write_process(self):
        self.ping_emulator()
        self._emulator.send(self.TX_commands.write_to_flash+'\n')
        self.wait_for_string('ready')

    def wait_for_string(self, string, timeout=2):
        t0 = time.time()
        data = ""
        while not (string in data):
            try:
                data += self._emulator.recv(1)
            except:
                pass
            #buff += data
            if time.time() - t0 > timeout:
                self.communicate('Timeout waiting for: "{}",\n'
                                'instead received "{}"'.format(string, data))
                break
            time.sleep(0.001)
        #self.communicate("EMU: '{}'".format(data))
        return data

    def _receive_and_process_data(self, _file, diode=None):
        data = self._receive_data(diode)
        if len(data) == self.eeprom_siz:
            _file = self.binary_parser.save_raw_data(data, _file)
            self.communicate("Receive data done")
            return _file
        else:
            msg = "Amount of received data is wrong. \n " \
                  "Expected size: {} \n Received: {}".format(self.eeprom_siz, len(data))
            self.communicate(msg)
            popup_window.warning_box(msg, detailed_msg="", title="Operation cancelled!")
            return None

    def _receive_data(self, diode):
        data = ''
        len_d = 0
        while len_d < self.eeprom_siz:
            try:
                data += self._emulator.recv(20)
            except:
                return data
            len_d = len(data)
            self.progress_signal(int(100 * float(len_d) / self.eeprom_siz))
        return data