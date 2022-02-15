
class DataSet():
    def __init__(self, sensorid):
        self.sensorid = sensorid
        self.data = []

    def datasize(self):
        return len(self.data)

    def addValue(self, value):
        self.data.append(value)

    def getJSON(self, bridge_name):
        # creating json like data
        data = {}
        data['bridgeid'] = str(bridge_name)
        data['sensorid'] = str(self.sensorid)
        data['datasize'] = 1
        data['data'] = ''.join(self.data)
        return data
