import json

class DataSet():
	def __init__(self, sensorid):
		self.sensorid = sensorid
		self.data = []

	def datasize(self):
		return len(self.data)

	def addValue(self, value):
		self.data.append(value)

	def getJSON(self):
		return json.dumps({
			'sensorid' : self.sensorid,
			'datasize' : self.datasize,
			'data' : self.data
			})
