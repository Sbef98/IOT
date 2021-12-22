def createMessageForArduino(flags, device_id, datasize, data):
	# prepare data, datasize depends whether we are working on
	# strings or not and therefor calculate it again

	byteData, datasize = getBytesForData(data)

	message = b'\xff'
	message += bytes([flags])
	message += bytes([int(device_id)])
	message += bytes([datasize])
	if(datasize > 0):
		message += byteData
	message += b'\xfe'
	print("Message to be send to arduino: ", message," with length: ", len(message))

	return message

def createDeviceInitializationMessage(device_id, sensor):
	if(sensor):
		return createMessageForArduino(flags=128, device_id=device_id, datasize=0, data=[])
	else:
		return createMessageForArduino(flags=(128 + 32), device_id=device_id, datasize=0, data=[])

def createActuatorNewValueMessage(device_id, data):
	return createMessageForArduino(flags=32, device_id=device_id, datasize=len(data), data=data)

def getBytesForData(data):
	newData = b''
	datasize = 0
	if isinstance(data, list):
		for item in data:
			newDataPoint, datasizeForPoint = getBytesForDatapoint(item)
			newData += newDataPoint
			datasize += datasizeForPoint
	else:
		newData, datasize = getBytesForDatapoint(data)

	return (newData, datasize)

def getBytesForDatapoint(datapoint):
	# handle integer and strings differently
	try:
		newBytes = bytes([int(datapoint)])
	except:
		newBytes = str.encode(datapoint)

	return (newBytes, len(newBytes))

class ProtocolBuffer:
	def __init__(self):
		self.inBuffer = []

	def readChar(self, receivedByte):
		if (receivedByte == b'\xfe') or (len(self.inBuffer) > 250): #EOL
			return True
		else:
			# append
			self.inBuffer.append (receivedByte)
			return False

	def isMessageCorrect(self):
		if len(self.inBuffer)<4:   # at least header, flags, sensorid, new sensor datatype, footer
			print("Warning: Message is shorter than minimum size")
			return False

			# split parts
		if self.inBuffer[0] != b'\xff': # first byte
			print("Warning: Start of sent data is incorrect")
			return False

		return True

	def isDebugMessage(self):
		flags = int.from_bytes(self.inBuffer[1], byteorder='little')
		if (flags & (1 << 6) == 64): # check whether second bit of flags is set
			return True
		return False

	def getFlags(self):
		return int.from_bytes(self.inBuffer[1], byteorder='little')

	def getMessageAsText(self):
		message = ""
		print("len inbuffer", len(self.inBuffer))
		print(self.inBuffer)
		for i in range(2, len(self.inBuffer)):
			try:
				message += self.inBuffer[i].decode("ascii")
			except:
				print("Print wrong character for: ",i , self.inBuffer[i])
		return message

	def isInitializationMessage(self):
		flags = int.from_bytes(self.inBuffer[1], byteorder='little')
		if (flags & (1 << 7) == 128):
			return True
		return False

	def isActuator(self):
		flags = int.from_bytes(self.inBuffer[1], byteorder='little')
		if (flags & (1 << 5) == 32):
			return True
		return False

	def getDataSize(self):
		return int.from_bytes(self.inBuffer[3], byteorder='little')

	def getDataType(self):
		datasize = self.getDataSize()
		datatype = ""
		for i in range(datasize):
			print(self.inBuffer[4+i])
			datatype += self.inBuffer[4 + i].decode("ascii")
		return datatype

	def getDeviceId(self):
		return int.from_bytes(self.inBuffer[2], byteorder='little')

	def getValue(self, position):
		return int.from_bytes(self.inBuffer[4 + position], byteorder='little')

	def cleanBuffer(self):
		self.inBuffer = []

