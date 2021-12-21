from sys import platform
from data import DataSet, ProtocolBuffer, createDeviceInitializationMessage

import requests
import serial
import serial.tools.list_ports
import socket, selectors, types

class CommunicationHandler():
# A CommunicationHandler is a class which should be a blue print for Handlers that want to communicate via
# different channels

    def __init__(self, bridge):
        self.bridge = bridge

        self.debug = False
        self.inbuffer = ProtocolBuffer()

    def loop(self):
    # The loop needs to be endless in order to run concurrently with the other jobs in the bridge
        while (True):
            pass

    def write(self, data, device_id = None):
    # receives data already in the correct format and sends it via the intended communication channel
        pass

    def useData(self):
        if not self.inbuffer.isMessageCorrect():
            return False

        print("Reading flags")

        if(self.inbuffer.isDebugMessage()):
            self.debug = True
            print("Debug message")

        print("Flags: ", self.inbuffer.getFlags())

        message = self.inbuffer.getMessageAsText()
        print("Message as text: " + message)

        if self.inbuffer.isInitializationMessage(): # check whether first bit of flags is set
            if self.inbuffer.isActuator():
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
        datasize = self.inbuffer.getDataSize()
        print(datasize)

        datatype = self.inbuffer.getDataType()
        print(datatype)

        data_json = {}
        data_json['bridgeid'] = str(self.bridge.name)

        data_json['sensor'] = "True" if sensor else "False"

        data_json['datatype'] = datatype
        print("json_data for initilization: ", data_json)

        if (not self.debug):
            print(self.bridge.cloud + '/adddevice')
            response = requests.post(self.bridge.cloud + '/adddevice', json=data_json)
            device_id = int(response.content) # TODO: answer in a nicer machine readable way
            print("device_id: ", device_id)

            if (sensor):
                self.bridge.sensors.append(device_id)
                print("Added sensor")
            else:
                self.bridge.actuators.append(device_id)
                print("Added actuator")

            data = createDeviceInitializationMessage(device_id, sensor)

            print(data)

            self.write(data, device_id) #check syntax
            print("Sent device_id to arduino",  device_id)
        else:
            print("Debug: Wanted to initialize sensor:", data_json)

    def addValueForSensor(self):
        sensorID = self.inbuffer.getSensorId()
        currentData = DataSet(sensorID)

        datasize = self.inbuffer.getDataSize()

        for i in range (datasize):
            try:
                val = self.inbuffer.getValue(i)
                currentData.addValue(val)
                strval = "Sensor %d: %d " % (sensorID, val)
                print(strval)
            except:
                print("Datasize not matching: ", datasize, len(self.inbuffer))

        # send the read data as json to the cloud
        data_json = currentData.getJSON(self.bridge.name)

        if(not self.debug):
            response = requests.post(self.bridge.cloud + '/addvalue', json=data_json)
            if (not response.ok):
                print("Something went wrong uploading the data. See statuscode " + response.reason)
        else:
            print("Debug: Wanted to send the following data to the cloud: ", data_json)


# https://realpython.com/python-sockets/#handling-multiple-connections
class SocketHandler(CommunicationHandler):
    def __init__(self,bridge, port, host):
        super().__init__(bridge)
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()

        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.lsock.bind((host, port))
        self.lsock.listen()
        print('listening on', (host, port))
        self.lsock.setblocking(False)
        self.sel.register(self.lsock, selectors.EVENT_READ, data=None)
        
        self.deviceConnections = {}
        
    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print('accepted connection from', addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, outb = ProtocolBuffer())
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data)
        
    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1)  # Should be ready to read
            if recv_data:
                if(data.outb.readChar(recv_data)):
                    print("\nValue received")
                    self.inbuffer = data.outb
                    self.useData()
                    self.deviceConnections[self.inbuffer.getDeviceId()] = sock
                    self.inbuffer.cleanBuffer()
                    data.outb.cleanBuffer()
            else:
                key_list = list(self.deviceConnections.keys())
                value_list = list(self.deviceConnections.values())
                
                key = key_list[value_list.index(sock)]
                
                print('closing connection to', data.addr, "Device id:", key)
                self.deviceConnections.pop(key)
                self.sel.unregister(sock)
                sock.close()
                
        # if mask & selectors.EVENT_WRITE:
        #     if data.outb:
        #         print('echoing', repr(data.outb), 'to', data.addr)
        #         sent = sock.send(data.outb)  # Should be ready to write
        #         data.outb = data.outb[sent:]

    def loop(self):
        while(True):
            events = self.sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                else:
                    self.service_connection(key, mask)
                    
    def write(self,data, device_id):
        print("Sending data")
        sock = self.deviceConnections[device_id]
        sock.send(data)


class SerialHandler(CommunicationHandler):

    def __init__(self, bridge):
        super().__init__(bridge)

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

                    message_ready = self.inbuffer.readChar(lastchar)

                    if message_ready:
                        print("\nValue received")
                        self.useData()
                        self.inbuffer.cleanBuffer()

    def write(self, bytes, device_id = None):
        self.ser.write(bytes)

if __name__ == "__main__":
    hand = SocketHandler(None, 8080, "localhost")
    SocketHandler.loop()
