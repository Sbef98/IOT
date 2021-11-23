
class Data():
	def __init__(self, sensorid):
		self.sensorid = sensorid
		self.data = []

	def datasize():
		return len(self.data)

	def addValue(self, value):
		self.data.append(value)
