import socket
import time
import binascii
import pycom
from network import LoRa

from CayenneLPP import CayenneLPP
from pytrack import Pytrack
from pycoproc import Pycoproc
from mq import MQ
from time import sleep

# Disable heartbeat LED
pycom.heartbeat(False)

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)

# create an OTAA authentication parameters
app_eui = binascii.unhexlify('70B3D57ED0011AF1')
app_key = binascii.unhexlify('C5010C0BA838A56930E77655A7FCADE7')

print("DevEUI: %s" % (binascii.hexlify(lora.mac())))
print("AppEUI: %s" % (binascii.hexlify(app_eui)))
print("AppKey: %s" % (binascii.hexlify(app_key)))
# Increment index used to scan each point from vector sensors_data
def inc(index, vector):
    if index < len(vector)-1:
        return index+1
    else:
        return 0
# Define your thread's behaviour, here it's a loop sending sensors data every 5 seconds
# join a network using OTAA (Over the Air Activation)
# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    pycom.rgbled(0x140000)
    time.sleep(2.5)
    pycom.rgbled(0x000000)
    time.sleep(1.0)
    print('Not yet joined...')

print('OTAA joined')
pycom.rgbled(0x001400)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

mq2 = MQ('P16')
while True:
    s.setblocking(True)
    pycom.rgbled(0x000014)
    lpp = CayenneLPP()
    print('\n\n** Mq8 Gas Sensor ppm value')
    value = mq2.MQRead()
    print('mq2_gas_ value', value)
    lpp.add_mq2(1, value)

    print('Sending data (uplink)...')
    s.send(bytes(lpp.get_buffer()))
    s.setblocking(False)
    data = s.recv(64)
    print('Received data (downlink)', data)
    pycom.rgbled(0x001400)
    time.sleep(30)
