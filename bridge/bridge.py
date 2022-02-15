#!/usr/bin/env python3

import asyncio
import time
from os import environ

from bridge.handler.message_management import createActuatorNewValueMessage

""" to see why I used requests and not urllib.request:
https://stackoverflow.com/questions/2018026/what-are-the-differences-between-the-urllib
-urllib2-urllib3-and-requests-modul"""
import requests

from bridge.handler import SerialHandler


class Bridge:

    def __init__(self, serial=True):
        self.debug = False
        self.name = 1  # Change when using a new bridge!
        self.cloud = 'http://127.0.0.1:5000'
        """generate token using:
        token = jwt.encode(
            {'public_id': self.name, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=8)}, 'my-secret')
        use secret from bridge"""
        self.accessToken = environ['ACCESS-TOKEN']

        self.sensors = []
        self.actuators = []

        if serial:
            self.serialHandler = SerialHandler(self)

        # internal input buffer for serial
        self.inbuffer = []

    def initialize(self):
        self.sendInitializeMessageToCloud()

    def sendInitializeMessageToCloud(self):
        data_json = {}
        data_json['bridgeid'] = str(self.name)
        self.sendToCloud('/initializebridge', data_json)
        print("Initialized Bridge")

    def sendToCloud(self, path, json_data):
        response = requests.post(
            self.cloud + '/' + path,
            json=json_data,
            headers={'x-access-tokens': self.accessToken})
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
                self.serialHandler.write(data)

                print("Sent actuator: ", actuator, "value: ", value)
                time.sleep(5)


if __name__ == '__main__':
    br = Bridge()
    br.initialize()
    br.loop()
