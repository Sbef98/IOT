#!/usr/bin/env python3

import asyncio
import time

""" to see why I used requests and not urllib.request:
https://stackoverflow.com/questions/2018026/what-are-the-differences-between-the-urllib
-urllib2-urllib3-and-requests-modul"""
import requests
from data import SerialHandler, DataSet, createActuatorNewValueMessage, \
    createDeviceInitializationMessage


class Bridge():

    def setup(self):
        self.debug = False
        self.name = 1  # Change when using a new bridge!
        self.cloud = 'http://127.0.0.1:8000'

        self.sensors = []
        self.actuators = []

        self.serialHandler = SerialHandler(self)

        # internal input buffer for serial
        self.inbuffer = []
        self.state = "addValueForSensor"

        self.sendInitializeMessageToCloud()

    def sendInitializeMessageToCloud(self):
        data_json = {}
        data_json['bridgeid'] = str(self.name)
        self.sendToCloud('initializebridge', data_json)
        print("Initialized Bridge")

    def sendToCloud(self, path, json_data):
        response = requests.post(self.cloud + '/' + path, json=json_data)
        return response

    async def asyncFunctions(self):
        # insert loops of communication handlers here
        callables = [self.serialHandler.loop, self.queryForNewActuatorValues]
        await asyncio.gather(*map(asyncio.to_thread, callables))

    def loop(self):

        loop = asyncio.get_event_loop()
        try:
            asyncio.run(self.asyncFunctions())
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()

    def useData(self, data):
        # I have received a line from the serial port. I can use it

        self.inbuffer = data

        if len(self.inbuffer) < 4:   # at least header, flags, sensorid, new sensor datatype, footer
            print("Warning: Message is shorter than minimum size")
            return False
        # split parts
        if self.inbuffer[0] != b'\xff':  # first byte
            print("Warning: Start of sent data is incorrect")
            return False

        print("Reading flags")

        flags = int.from_bytes(self.inbuffer[1], byteorder='little')

        if flags & (1 << 6) == 64:  # check whether second bit of flags is set
            self.debug = True
            print("Debug message")

        print("Flags: ", flags)

        message = ""
        for i in range(2, len(self.inbuffer)):
            try:
                message += self.inbuffer[i].decode("ascii")
            except:
                print("Print wrong character for: ", i, self.inbuffer[i])
        print("Message as text: " + message)

        if flags & (1 << 7) == 128:  # check whether first bit of flags is set
            if flags & (1 << 5) == 32:
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
            print(self.inbuffer[4 + i])
            datatype += self.inbuffer[4 + i].decode("ascii")

        data_json = {}
        data_json['bridgeid'] = str(self.name)

        data_json['sensor'] = "True" if sensor else "False"

        data_json['datatype'] = datatype
        print("json_data for initilization: ", data_json)

        if (not self.debug):
            response = self.sendToCloud('adddevice', data_json)
            device_id = int(response.content)  # TODO: answer in a nicer machine readable way

            if(device_id > 253):
                print("""Warning: to many devices initialized for that bridge and
                 device id to high for serial communication""")
                return

            if sensor:
                flags = 128
                self.sensors.append(device_id)
            else:
                flags = 32 + 128
                self.actuators.append(device_id)
                print("Added actuator")

            data = createDeviceInitializationMessage(flags, device_id)

            self.serialHandler.write(data)
            print("Sent device_id to arduino", device_id)
        else:
            print("Debug: Wanted to initialize sensor:", data_json)

    def addValueForSensor(self):
        sensorID = int.from_bytes(self.inbuffer[2], byteorder='little')
        currentData = DataSet(sensorID)

        datasize = int.from_bytes(self.inbuffer[3], byteorder='little')

        for i in range(datasize):
            try:
                val = int.from_bytes(self.inbuffer[4 + i], byteorder='little')
                currentData.addValue(val)
                strval = "Sensor %d: %d " % (sensorID, val)
                print(strval)
            except:
                print("Datasize not matching: ", datasize, len(self.inbuffer))

        # send the read data as json to the cloud
        data_json = currentData.getJSON(self.name)

        if(not self.debug):
            response = self.sendToCloud('addvalue', data_json)
            if (not response.ok):
                print("Something went wrong uploading the data. See statuscode " + response.reason)
        else:
            print("Debug: Wanted to send the following data to the cloud: ", data_json)

    def queryForNewActuatorValues(self):
        while True:
            time.sleep(30)

            data_json = {}
            data_json['bridgeid'] = str(self.name)
            data_json['actuator_num'] = str(len(self.actuators))
            data_json['actuators'] = [str(actuator) for actuator in self.actuators]
            response = self.sendToCloud('getNewValues', data_json)

            # expecting json like {'actuator_number' : 'actuator_value'}
            print("Queried cloud for new Values for actuators")

            actuators = response.json()

            print("Answer:", actuators)

            for actuator in actuators:
                value = actuators[actuator]
                data = createActuatorNewValueMessage(actuator, value)
                self.ser.write(data)

                print("Sent actuator: ", actuator, "value: ", value)
                time.sleep(5)


if __name__ == '__main__':
    br = Bridge()
    br.setup()
    br.loop()
