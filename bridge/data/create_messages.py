
def createMessageForArduino(flags, device_id, datasize, data):
	# Note: datasize > 1 needs to be fixed
	message = b'\xff'
	message = message + bytes([flags])
	message = message + bytes([int(device_id)])
	message = message + bytes([datasize])
	if(datasize > 0):
		message = message + bytes([int(data)])
	message = message + b'\xfe'
	print("Message to be send to arduino: ", message," with length: ", len(message))

	return message

def createDeviceInitializationMessage(flags, device_id):
	return createMessageForArduino(flags=flags, device_id=device_id, datasize=0, data={})

def createActuatorNewValueMessage(device_id, data):
	return createMessageForArduino(flags=32, device_id=device_id, datasize=len(data), data=data)
