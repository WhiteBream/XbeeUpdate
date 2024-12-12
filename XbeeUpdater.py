#!/usr/bin/python
# XBee firmware update script Copyright (C) 2024, White Bream

import sys
import time

from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee16BitAddress, XBee64BitAddress, XBeeException, XBeeProtocol
import serial

PORT = 'COM6'

firmware_type = XBeeProtocol.ZIGBEE
firmware_name = 'XB3-24Z/XB3-24Z_1013'
firmware_ver = 0x1013
#firmware_type = XBeeProtocol.RAW_802_15_4
#firmware_name = 'XB3-24A/XB3-24A_2012'
#firmware_ver = 0x2012
#firmware_type = XBeeProtocol.DIGI_MESH 
#firmware_name = 'XB3-24DM/XB3-24DM_3012'
#firmware_ver = 0x3012

def XbeeConnect():
  global device
  try:
    device.close()
  except:
    pass
  try:
    ser = serial.Serial(PORT, 9600, timeout=2)
    time.sleep(1)
    ser.write(b'+++')  # Enter command mode
    ser.read_until(b'\r')
    ser.write(b'ATAP2\r')
    ser.read_until(b'\r')
    ser.write(b'ATBD7\r') # 115K2
    ser.read_until(b'\r')
    ser.write(b'ATCN\r')
    ser.close()
    device = XBeeDevice(PORT, 115200)  # connect with FTDI
    device.open()  # connect with XB3
  except Exception as e:
    print(repr(e), end='', flush=True)


def xbeeFirmware():
  global device
  try:
    XbeeConnect()
    rev1 = device.get_firmware_version()
    rev1 = ''.join(f'{byte:02X}' for byte in rev1)
    protocol1 = device.get_protocol()
    str = protocol1.name + ' v' + rev1
    if protocol1.code != firmware_type or int(rev, 16) < firmware_ver:
      print('Firmware ' + str + ' update to ' + firmware_name + ' ... ')
      device.update_firmware(firmware_name + '.xml',
                         xbee_firmware_file = firmware_name + '.gbl',
                         bootloader_firmware_file = 'XB3-boot-rf/xb3-boot-rf_1.11.2.gbl')
      device.close()
      time.sleep(1)
      XbeeConnect()
      rev2 = device.get_firmware_version()
      rev2 = ''.join(f'{byte:02X}' for byte in rev2)
      protocol2 = device.get_protocol()
      if protocol1.code != protocol2.code:
        str = protocol2.name + ' v' + rev2 + ' (from ' + str + ')'
      else:
        str = protocol2.name + ' v' + rev2 + ' (from v' + rev1 + ')'
    print(str)
  except XBeeException:
    device.close()
    XbeeConnect()
    print('try again')
  except Exception as e:
    print(repr(e))


print(f'XBee firmware update, Copyright (C) 2024, White Bream')

if "--p" in sys.argv:
    PORT = sys.argv[sys.argv.index("--p") + 1]

xbeeFirmware()  # Takes a long time, probably a minute or two!
print('Bye')
  
