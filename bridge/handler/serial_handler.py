from sys import platform

import serial
import serial.tools.list_ports


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
                        self.bridge.useData(self.inbuffer)
                        self.inbuffer =[]
                    else:
                        # append
                        self.inbuffer.append (lastchar)

    def write(self, bytes):
        self.ser.write(bytes)
