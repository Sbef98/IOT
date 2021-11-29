#!/usr/bin/env python3

from data import DataSet
# to see why I used requests and not urllib.request:
# https://stackoverflow.com/questions/2018026/what-are-the-differences-between-the-urllib-urllib2-urllib3-and-requests-modul
import requests
import serial
import serial.tools.list_ports
from sys import platform
import warnings

class Bridge():

    def setup(self):
        # open serial port
        self.ser = None
        print('list of available ports: ')

        ports = serial.tools.list_ports.comports()
        self.portname=None
        
        # finding correct serial port and connecting
        for port in ports:
            print (port.device)
            print (port.description)
            if (platform == 'linux' and 'seeeduino' in port.description.lower()) or (platform == 'win32' and 'com4' in port.description.lower()):
                self.portname = port.device
                print ("connecting to " + self.portname)
                break
        try:
            if self.portname:
                print("Portname:" + self.portname)
                # self.ser = serial.Serial(self.portname, 9600, timeout=0)
                self.ser =serial.Serial(self.portname)
                print("self.ser:" + self.ser.name)
        except:
            self.ser = None
            print("not connected")

        # internal input buffer for serial
        self.inbuffer = []
        self.state = "addValueForSensor"

    def loop(self):
        # infinite loop for serial managing
        
        while (True):
            # print(self.ser)
            # look for a byte from serial
            if self.ser:
                if self.ser.in_waiting>0:
                    # data available from the serial port
                    lastchar=self.ser.read(1)

                    if lastchar==b'\xfe' or len(self.inbuffer) > 250: #EOL
                        print("\nValue received")
                        self.useData()
                        self.inbuffer =[]
                    else:
                        # append
                        self.inbuffer.append (lastchar)

    def useData(self):
        # I have received a line from the serial port. I can use it
        if len(self.inbuffer)<4:   # at least header, flags, new sensor datatype, footer
            warning.warn("Message has is shorter than minimum size")
            return False
        # split parts
        if self.inbuffer[0] != b'\xff': # first byte
            warning.warn("Start of sent data is incorrect")
            return False

        print("reading flags")

        flags = int.from_bytes(self.inbuffer[1], byteorder='little')
        if (flags & (1 << 7) == 128): # check whether first bit of flags is set
            self.state = "newSensor"
            self.initializeSensor()
        elif (flags & (1 << 6) == 64): # check whether second bit of flags is set
            self.state = "debugMode"
            print("Debug message")
        else:
            self.state = "addValueForSensor"
            self.addValueForSensor()

    def initializeSensor(self):
        data = bytearray(b'\xff')
        data.append(115) # TODO: think about sensor ids
        data.append(244) # equals b'\xfe' as stop sign
        self.ser.write(data)

    def addValueForSensor(self):
        sensorID = int.from_bytes(self.inbuffer[2], byteorder='little')
        currentData = DataSet(sensorID)

        datasize = int.from_bytes(self.inbuffer[3], byteorder='little')

        for i in range (datasize):
            val = int.from_bytes(self.inbuffer[4 + i], byteorder='little')
            currentData.addValue(val)
            strval = "Sensor %d: %d " % (sensorID, val)
            print(strval)

        # send the read data as json to the cloud
        data_json = currentData.getJSON()
        response = requests.post('http://0.0.0.0:80/addvalue', json=data_json)
        if (not response.ok):
            print("Something went wrong uploading the data. See statuscode " + response.reason)

if __name__ == '__main__':
    br=Bridge()
    br.setup()
    br.loop()            
