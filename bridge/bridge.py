import serial
import serial.tools.list_ports
# to see why I used requests and not urllib.request:
# https://stackoverflow.com/questions/2018026/what-are-the-differences-between-the-urllib-urllib2-urllib3-and-requests-modul
import requests

class Bridge():

    def setup(self):
	    # TODO: copied - what do we really need?
        # open serial port
        self.ser = None
        print("list of available ports: ")

        ports = serial.tools.list_ports.comports()
        self.portname=None
        for port in ports:
            print (port.device)
            print (port.description)
            if 'com4' in port.description.lower():
                self.portname = port.device
                print ("connecting to " + self.portname)
        try:
            if self.portname:
                print("Portname:" + self.portname)
                # self.ser = serial.Serial(self.portname, 9600, timeout=0)
                self.ser =serial.Serial(self.portname)
                print("self.ser:" + self.ser.name)
        except:
            self.ser = None

        # self.ser.open()

        # internal input buffer from serial
        self.inbuffer = []

    def loop(self):
    	# TODO: see what we really need
        # infinite loop for serial managing
        
        while (True):
            #print(self.ser)
            #look for a byte from serial
            if self.ser:
                #print("serial is not none")

                if self.ser.in_waiting>0:
                    # data available from the serial port
                    lastchar=self.ser.read(1)

                    if lastchar==b'\xfe': #EOL
                        print("\nValue received")
                        self.useData()
                        self.inbuffer =[]
                    else:
                        # append
                        self.inbuffer.append (lastchar)

    def useData(self):
    	# TODO: see what we really need
        # I have received a line from the serial port. I can use it
        if len(self.inbuffer)<3:   # at least header, size, footer
            return False
        # split parts
        if self.inbuffer[0] != b'\xff':
            return False

        numval = int.from_bytes(self.inbuffer[1], byteorder='little')
        for i in range (numval):
            val = int.from_bytes(self.inbuffer[i+2], byteorder='little')
            strval = "Sensor %d: %d " % (i, val)
            print(strval)
            response = requests.post('http://155.185.73.84:80/addvalue/'+ str(val))
            if (not response.ok):
            	print("Something went wrong uploading the data. See statuscode " + response.reason)

if __name__ == '__main__':
    br=Bridge()
    br.setup()
    br.loop()            