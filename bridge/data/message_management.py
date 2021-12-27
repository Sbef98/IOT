import types

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

"""
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
"""
def emptyProtocolInBuffer():
    return types.SimpleNamespace(data = [], flags = -1, device_id = -1, data_length = 0)

class ProtocolValsIterator:
    """ Useful for iterating over the values inside this buffer """
    def __init__(self, buff):
        self._buffer = buff
        self._index = 0

    def __next__(self):
        if self._index < self._buffer.data_length:
            self._index += 1
            return self._buffer.data[self._index]
        else:
            raise StopIteration


class ProtocolBuffer:

    def __init__(self, beginTrigger = b'\xff', endTrigger = b'\xfe'):
        self.inBuffer = emptyProtocolInBuffer()
        self.beginTrigger = beginTrigger
        self.endTrigger = endTrigger

    def readChar(self, val):
        """
        Meant to be used in a loop to read a sequence of bytes,
        needs to be implemented better!
        """

        if (val == self.endTrigger): #EOLi
            return True

        elif (val == self.beginTrigger):
            self.inBuffer = emptyProtocolInBuffer()
            return False

        else:
            if(self.inBuffer.flags == -1):
                self.inBuffer.flags = val

            elif(self.inBuffer.device_id == -1):
                self.setDeviceId(val)

            else:
                self.addValue(val)

            if(self.inBuffer.data_length > 250): #EOL
                return True

            else:
                return False

    def __iter__(self):
        return ProtocolsValsIterator(self.inBuffer)

    def getValue(self, pos):
        if(self.inBuffer.data_length <= pos or pos < 0):
            raise IndexError
        else:
            return self.inBuffer.data[pos]

    def addValue(self, val):
        """ Meant to be used to add a value to an existing message """

        if(val == self.beginTrigger):
            exceptionString = "Cannot add " + self.beginTrigger + " value within data section"
            raise Exception(exceptionString)

        elif(val == self.endTrigger):
            excceptionString = "Cannot add " + self.endTrigger + " value within data section"
            raise Exception(exceptionString)

        elif(self.inBuffer.data_length > 250):
            raise Exception("Adding too many bytes to the data section!")

        else:
            self.inBuffer.data.append(val)
            self.inBuffer.data_length += 1

    def setInitializationFlag(self, boolean):
        if self.inBuffer.flags & (1 << 7) == 128:  # Checking if it was already set
            if(boolean == True):                    # If yes leave as is
                return
            else:
                self.inBuffer.flags -= 128          # Else take off the flag
        else:
            if(boolean == True):                    # Same here but inverted
                self.inBuffer.flags += 128
            else:
                return

    def isInitializationMessage(self):
        if self.inBuffer.flags & (1 << 7) == 128:
            return True
        else:
            return False


    def setDebugFlag(self, boolean):
        if self.inBuffer.flags & (1 << 6) == 64:  # Checking if it was already set
            if(boolean == True):                    # If yes leave as is
                return
            else:
                self.inBuffer.flags -= 64          # Else take off the flag
        else:
            if(boolean == True):                    # Same here but inverted
                self.inBuffer.flags += 64
            else:
                return

    def isDebugMessage(self):
        if self.inBuffer.flags & (1 << 6) == 64:
            return True
        else:
            return False


    def setActuatorFlag(self,boolean):
        if self.inBuffer.flags & (1 << 5) == 32:  # Checking if it was already set
            if(boolean == True):                    # If yes leave as is
                return
            else:
                self.inBuffer.flags -= 32          # Else take off the flag
        else:
            if(boolean == True):                    # Same here but inverted
                self.inBuffer.flags += 32
            else:
                return
    def isActuatorMessage(self):
        if self.inBuffer.flags & (1 << 5) == 32:
            return True
        else:
            return False


    def setDeviceId(self, device_id):
        self.inBuffer.device_id = device_id

    def getDeviceId(self):
        return self.inBuffer.device_id

    def getDataSize(self):
        return self.inBuffer.data_length

    def getDataAsList(self):
        return self.inBuffer.data

    def getDataAsString(self, debug = False):
        message = ""
        for i in range(0, len(self.inBuffer.data)):
            if(self.inBuffer.data[i] == 0): #in this case it's a 0 ending string, so it actually finishes here!
                return message
            try:
                message += self.inBuffer.data[i].decode("ascii")
            except:
                if(debug == True):
                    print("Wrong character for:",i,self.inBuffer.data[i])
        return message

    def flushBuffer(self):
        self.inBuffer = emptyProtocolInBuffer()

    def isMessageCorret(self):

        if(self.inBuffer.flags < 0):
            return False, "noFlags"

        if(self.inBuffer.device_id < 0):
            return False, "noDeviceId"

        if(self.inBuffer.data_length < 0):
            return False, "noDataLength"

        if(self.inBuffer.data_length != len(self.inBuffer.data)):
            return False, "incorrectDataLength"

        return True

    def toString(self):
        stringozza = "Flags active: \n\r"
        stringozza += "\t - Debug: " + str(self.isDebugMessage()) +"\n\r"
        stringozza += "\t - Actuator: " + str(self.isInitializationMessage()) +"\n\r"
        stringozza += "\t - Initialization: " + str(self.isActuatorMessage()) +"\n\r"
        stringozza += "Device ID: " + str(self.getDeviceId()) + "\n\r"
        stringozza += "Data Length: " + str(self.getDataSize()) + "\n\r"
        stringozza += "Data: " + str(self.getDataAsList()) + "\n\r"
        return stringozza

class InitializationBuffer(ProtocolBuffer):
    def __init__(self):
        super().__init__()
    def getDataType():
        return self.gedDataAsString()


if __name__ == "__main__":
    buff = ProtocolBuffer()
    print(buff.toString())
    buff.readChar(b'\xff')
    buff.readChar(128+32)
    buff.readChar(10)
    buff.readChar(5)
    buff.readChar(b'c')
    buff.readChar(b'i')
    buff.readChar(b'a')
    buff.readChar(b'o')
    buff.readChar(0)

    if(buff.readChar(b'\xfe')):
        print(buff.toString())

    buff.setDeviceId(10)

    print(buff.toString())
