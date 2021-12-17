from sys import platform

import serial
import serial.tools.list_ports
import socket

class CommunicationHandler():
# A CommunicationHandler is a class which should be a blue print for Handlers that want to communicate via
# different channels

    def __init__(self, bridge):
    # In the initialization the Communication handler can start setting up everything to receive communication

        # in order for the handler to speak to the bridge or to call a method there we store a reference to the bridge
        self.bridge = bridge

        # set up communication requirements here

    def loop(self):
    # The loop needs to be endless in order to run concurrently with the other jobs in the bridge
        while (True):
            pass

    def write(self, data):
    # receives data already in the correct format and sends it via the intended communication channel
        pass

# https://realpython.com/python-sockets/#handling-multiple-connections
class SocketHandler(CommunicationHandler):
    def __init__(self,bridge, port, host):
        super().__init__(bridge)
        self.host = host
        self.port = port

        with socket.socket(socker.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host,self.port))
            s.listen()
            print("Listening on:",(self.host,self.port))

    def loop(self):
        pass
    def write(self,data):
        pass


class SerialHandler(CommunicationHandler):

    def __init__(self, bridge):
        super().__init__(bridge)

        self.inbuffer = []

        # open serial port
        self.ser = None
        print('list of available ports: ')

        ports = serial.tools.list_ports.comports()
        self.portname=None
        
        # finding correct serial port and connecting
        for port in ports:
            print (port.device)
            print (port.description)
            if (platform == 'linux' and ('seeeduino' or 'leonardo' or 'usb') in port.description.lower()) or (platform == 'win32' and 'com4' in port.description.lower()):
                self.portname = port.device
                print ("connecting to " + self.portname)
                break
        try:
            if self.portname:
                print("Portname:" + self.portname)
                self.ser =serial.Serial(self.portname)
                print("self.ser:" + self.ser.name)
        except:
            self.ser = None
            print("not connected")

    def loop(self):
        while (True):
            # look for a byte from serial
            if self.ser:
                if self.ser.in_waiting>0:
                    # data available from the serial port
                    lastchar=self.ser.read(1)

                    if lastchar==b'\xfe' or len(self.inbuffer) > 250: #EOL
                        print("\nValue received")
                        self.bridge.useData()
                        self.inbuffer =[]
                    else:
                        # append
                        self.inbuffer.append (lastchar)

    def write(self, bytes):
        self.ser.write(bytes)

    def useData(self):
        
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
            if (flags & (1 << 5) == 32):
                self.state = "newActuator"
                print("Initialize Actuator")
                self.initializeDevice(sensor=False)
            else:
                self.state = "newSensor"
                print("Initialize Sensor")
                self.initializeDevice(sensor=True)
            
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

        data_json['sensor'] = "True" if sensor else "False"
    
        data_json['datatype'] = datatype
        print("json_data for initilization: ", data_json)

        if (not self.debug):
            response = requests.post(self.cloud + '/adddevice', json=data_json)
            device_id = int(response.content) # TODO: answer in a nicer machine readable way
            
            if (sensor):
                flags = 128
                self.sensors.append(device_id)
            else:
                flags = 32 + 128
                self.actuators.append(device_id)
                print("Added actuator")

            data = createDeviceInitializationMessage(flags, device_id)
            
            self.serialHandler.write(data)
            print("Sent device_id to arduino",  device_id)
        else:
            print("Debug: Wanted to initialize sensor:", data_json)

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
            print("Debug: Wanted to send the following data to the cloud: ", data_json)


