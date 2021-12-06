#!/usr/bin/env python3

from data import DataSet
# to see why I used requests and not urllib.request:
# https://stackoverflow.com/questions/2018026/what-are-the-differences-between-the-urllib-urllib2-urllib3-and-requests-modul
import requests
import serial
import serial.tools.list_ports
from sys import platform

class Bridge():

    def setup(self):
        self.debug = False
        self.name = 1 # Change when using a new bridge!
        self.cloud = 'http://127.0.0.1:8000'

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
        if len(self.inbuffer)<4:   # at least header, flags, sensorid, new sensor datatype, footer
            print("Warning: Message is shorter than minimum size")
            return False
        # split parts
        if self.inbuffer[0] != b'\xff': # first byte
            print("Warning: Start of sent data is incorrect")
            return False

        print("Reading flags")

        flags = int.from_bytes(self.inbuffer[1], byteorder='little')

        if (flags & (1 << 6) == 64): # check whether second bit of flags is set
            self.debug = True
            print("Debug message")

        print("Flags: ", flags)

        message = ""
        for i in range(2, len(self.inbuffer)):
            try:
                message += self.inbuffer[i].decode("ascii")
            except:
                print("Print wrong character for: ",i , self.inbuffer[i])
        print("Message as text: " + message)

        if (flags & (1 << 7) == 128): # check whether first bit of flags is set
            self.state = "newSensor"
            print("Initialize Sensor")
            self.initializeDevice(sensor=True)
        elif (flags & (1 << 5) == 32):
            self.state = "newActuator"
            print("Initialize Actuator")
            self.initializeDevice(sensor=False)
        else:
            self.state = "addValueForSensor"
            print("Add Value for Sensor")
            self.addValueForSensor()

    def initializeDevice(self, sensor):
        # read string from inbuffer until fe
        # FF Flags sensorid=0 datasize datatype_as_string FE
        datasize = int.from_bytes(self.inbuffer[3], byteorder='little')
        
        datatype = ""
        for i in range(datasize):
            print(self.inbuffer[4+i])
            datatype += self.inbuffer[4 + i].decode("ascii")

        data_json = {}
        data_json['bridge'] = str(self.name)
        if (sensor):
            data_json['sensor'] = "True"
        else:
            data_json['sensor'] = "False"
        data_json['datatype'] = datatype
        print("json_data for initilization: ", data_json)

        if (not self.debug):
            response = requests.post(self.cloud + '/adddevice', json=data_json)
            device_id = int(response.content) # TODO: answer in a nicer machine readable way
            
            if (sensor):
                flags = 128
            else:
                flags = 32

            data = bytearray(b'\xff')
            data.append(flags)
            data.append(device_id) 
            data.append(00) # datasize is zero
            data.append(254) # equals b'\xfe' as stop sign
            print(data, len(data))
            
            self.ser.write(data)
            print("Sent sensor_id to arduino",  device_id)
        else:
            print("Wanted to initialize sensor:", data_json)

    def addValueForSensor(self):
        sensorID = int.from_bytes(self.inbuffer[2], byteorder='little')
        currentData = DataSet(sensorID)

        datasize = int.from_bytes(self.inbuffer[3], byteorder='little')

        for i in range (datasize):
            try:
                val = int.from_bytes(self.inbuffer[4 + i], byteorder='little')
                currentData.addValue(val)
                strval = "Sensor %d: %d " % (sensorID, val)
                print(strval)
            except:
                print("Datasize not matching: ", datasize, len(self.inbuffer))

        # send the read data as json to the cloud
        data_json = currentData.getJSON()

        if(not self.debug):
            response = requests.post(self.cloud + '/addvalue', json=data_json)
            if (not response.ok):
                print("Something went wrong uploading the data. See statuscode " + response.reason)
        else:
            print("Wanted to send the following data to the cloud: ", data_json)

if __name__ == '__main__':
    br=Bridge()
    br.setup()
    br.loop()            
