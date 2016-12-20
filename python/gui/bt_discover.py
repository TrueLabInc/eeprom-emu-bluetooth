import bluetooth
import time

def search(device='BT_EEPROM_EMULATOR'):
    timeout = 20
    device_name = ''
    t0 = time.time()
    while device_name != device:
        if time.time() - t0 > timeout:
            print "Timeout"
            break
        print '.',
        devices = bluetooth.discover_devices(lookup_names = True)
        for x in devices:
            device_name = x[1]
            device_address = x[0]
            #print x        # <--

    return device_name, device_address

print search('BT_EEPROM_EMULATOR')