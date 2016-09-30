import sys
import pynmea2
from serial import Serial

ser = Serial()
ser.baudrate = 9600
ser.port = '/dev/ttyUSB0'

ser.open()
   
if not ser.isOpen():
   print("Unable to open serial port!")
   raise SystemExit
   
reader = pynmea2.NMEAStreamReader()
   
while True:
   raw = ser.readline()
   if raw[0] == 36:
      gps = raw.decode("ascii") 
      msg = pynmea2.parse(gps)
      print("MSG: {0}/{1}".format(msg.talker, msg.sentence_type))
