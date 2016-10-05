from serial.tools import list_ports
from collections import OrderedDict
import platform

class FindUsbDevice:
    def __init__(self, platform_type):
        self.platform_name = platform_type
        #print '{} {}'.format('Detected platform', self.platform_name)
        self.serial_description_linux = [
            'product',
            'serial_number',
            'manufacturer',
            'description',
            'device',
            'device_path',
            'hwid',
            'location',
            'name',
            'pid',
            'subsystem',
            'usb_device_path',
            'vid'
        ]
        self.serial_description_win = [
            'name',
            'description',
            'product'
        ]
    #     self.path = bin_path
    #     self.rx_buffer_size = 64
    #     self.digitool_serial_port = "//dev//ttyUSB0"
    #     self.digitool_baud_rate = 250000
    #     self.digi_tool_serial = None
    #     self.verbose_mode = False
    #     os.system("clear")
    #     self.welcome()
    def find_serial_devices(self):
        return list_ports.comports()

    def device_description(self, device):
        description = OrderedDict()
        if self.platform_name == 'Linux':
            for i in self.serial_description_linux:
                description[i] = getattr(device, i)
        else:
            for i,label in enumerate(self.serial_description_win):
                description[label] = device[i]
            description['device'] = description['name']
        return description

    def get_devices_info(self):
        descriptions = {}
        devices = self.find_serial_devices()
        for d in devices:
            tmp = self.device_description(d)
            descriptions[tmp['name']] = tmp
        return descriptions

    def print_devices_info(self):
        devices = self.get_devices_info()
        footer_len = 0
        print
        for d in devices:
            dev = devices[d]
            for item in devices[d]:
                #print item, dev[item]
                print '{:20}: {}'.format(item, dev[item])
                l = len(str(dev[item]))
                if l > footer_len:
                    footer_len = l
            print '-'*footer_len
