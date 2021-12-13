
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

def createDeviceInitializationMessage(flags, device_id):
	return createMessageForArduino(flags=flags, device_id=device_id, datasize=0, data=[])

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
