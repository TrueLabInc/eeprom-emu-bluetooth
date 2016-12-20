__author__ = 'rafal'

# serial_commands_rx = {
#     "digiToolRxBufferReady": 0x7,
#     "blankTestFail": 2,
#     "blankTestPass": 1,
#     "sendingData":   3,
#     "writeFailed":   4,
#     "cpuLoad":      5,
#     "memUsage":     6,
# }
#
# serial_commands_rx_errors = {
#     4: "write failed",
#     2: "blank test failed",
# }
#
# serial_commands_tx = {
#     "handshake":  'c',
#     "write_eeprom": 'w',
#     "read_eeprom":  'r',
#     "cpu_load":    'C',
#     "call": 'c\n',
# }

class TX_commands:
    def __init__(self):
        self.call = 'c'
        self.write_to_flash = 'write'
        self.serial_test = 'test'
        self.reset = 'reset'
        self.read_sram = 'sramRd'
        self.read_flash = 'flashRd'
        self.write_single_byte = 'w'
        self.keep_awake = 'awake'
        self.let_sleep = 'sleep'
        self.get_flash_stats = 'bank'
        self.bank1 = 'bank1'
        self.bank2 = 'bank2'
        self.bank3 = 'bank3'
        self.get_flash_wear = 'fwear'
        self.read_single_byte = 'r'
        self.ping_cmd = 'p'
        self.ack = '.'

class RX:
    def __init__(self):
        pass

class Commands:
    def __init__(self):
        self.tx = TX()
        self.rx = RX()

