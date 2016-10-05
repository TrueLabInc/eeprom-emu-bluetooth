__author__ = 'rafal'

serial_commands_rx = {
    "digiToolRxBufferReady": 0x7,
    "blankTestFail": 2,
    "blankTestPass": 1,
    "sendingData":   3,
    "writeFailed":   4,
    "cpuLoad":      5,
    "memUsage":     6,
}

serial_commands_rx_errors = {
    4: "write failed",
    2: "blank test failed",
}

serial_commands_tx = {
    "write_eeprom": 'w',
    "read_eeprom":  'r',
    "cpu_load":    'C',
    "call": 'c\n',
}
