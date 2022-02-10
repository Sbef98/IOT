import types


def emptyProtocolInBuffer():
    return types.SimpleNamespace(data=[], flags=-1, sent_data_size=None, device_id=-1, data_length=0)


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

    def __init__(self, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        self.inBuffer = emptyProtocolInBuffer()
        self.beginTrigger = beginTrigger
        self.endTrigger = endTrigger

    def readChar(self, val):
        """
        Meant to be used in a loop to read a sequence of bytes,
        needs to be implemented better!
        """

        if val == self.endTrigger:  # EOLi
            return True

        elif val == self.beginTrigger:
            self.inBuffer = emptyProtocolInBuffer()
            return False

        else:
            if self.inBuffer.flags == -1:
                self.inBuffer.flags = int.from_bytes(val, byteorder='little')

            elif self.inBuffer.device_id == -1:
                self.setDeviceId(int.from_bytes(val, byteorder='little'))

            elif not self.inBuffer.sent_data_size:
                self.inBuffer.sent_data_size = int.from_bytes(val, byteorder='little')

            else:
                self.addValue(val)

            if self.inBuffer.data_length > 250:  # EOL
                return True

            else:
                return False

    def __iter__(self):
        return ProtocolValsIterator(self.inBuffer)

    def getValue(self, pos):
        if self.inBuffer.data_length <= pos or pos < 0:
            raise IndexError
        else:
            return self.inBuffer.data[pos]

    def addValue(self, val):
        """ Meant to be used to add a value to an existing message """

        if val == self.beginTrigger:
            exceptionString = "Cannot add " + self.beginTrigger + " value within data section"
            raise Exception(exceptionString)

        elif val == self.endTrigger:
            excceptionString = "Cannot add " + self.endTrigger + " value within data section"
            raise Exception(excceptionString)

        elif self.inBuffer.data_length > 250:
            raise Exception("Adding too many bytes to the data section!")

        else:
            self.inBuffer.data.append(val)
            self.inBuffer.data_length += 1

    def setInitializationFlag(self, boolean):
        if self.inBuffer.flags & (1 << 7) == 128:  # Checking if it was already set
            if boolean:                    # If yes leave as is
                return
            else:
                self.inBuffer.flags -= 128          # Else take off the flag
        else:
            if boolean:                    # Same here but inverted
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
            if boolean:                    # If yes leave as is
                return
            else:
                self.inBuffer.flags -= 64          # Else take off the flag
        else:
            if boolean:                    # Same here but inverted
                self.inBuffer.flags += 64
            else:
                return

    def isDebugMessage(self):
        if self.inBuffer.flags & (1 << 6) == 64:
            return True
        else:
            return False

    def setActuatorFlag(self, boolean):
        if self.inBuffer.flags & (1 << 5) == 32:  # Checking if it was already set
            if boolean:                    # If yes leave as is
                return
            else:
                self.inBuffer.flags -= 32          # Else take off the flag
        else:
            if boolean:                    # Same here but inverted
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

    def getDataAsString(self, debug=False):
        message = ""
        for i in range(0, len(self.inBuffer.data)):
            if self.inBuffer.data[i] == 0:  # in this case it's a 0 ending string, so it actually finishes here!
                return message
            try:
                message += self.inBuffer.data[i].decode("ascii")
            except:
                if debug:
                    print("Wrong character for:", i, self.inBuffer.data[i])
        return message

    def flushBuffer(self):
        self.inBuffer = emptyProtocolInBuffer()

    def isMessageCorrect(self):

        if self.inBuffer.flags < 0:
            return False, "noFlags"

        if self.inBuffer.device_id < 0:
            return False, "noDeviceId"

        if self.inBuffer.data_length < 0:
            return False, "noDataLength"

        if self.inBuffer.data_length != len(self.inBuffer.data):
            return False, "incorrectDataLength"

        return True

    def toString(self):
        message = "Flags active: \n\r"
        message += "\t - Debug: " + str(self.isDebugMessage()) + "\n\r"
        message += "\t - Actuator: " + str(self.isInitializationMessage()) + "\n\r"
        message += "\t - Initialization: " + str(self.isActuatorMessage()) + "\n\r"
        message += "Device ID: " + str(self.getDeviceId()) + "\n\r"
        message += "Data Length: " + str(self.getDataSize()) + "\n\r"
        message += "Data: " + str(self.getDataAsList()) + "\n\r"
        return message

    def getDataType(self):
        if self.isInitializationMessage():
            return self.getDataAsString()
        else:
            return None


class InitializationBuffer(ProtocolBuffer):
    def __init__(self):
        super().__init__()

    def getDataType(self):
        return self.gedDataAsString()


if __name__ == "__main__":
    buff = ProtocolBuffer()
    print(buff.toString())
    buff.readChar(b'\xff')
    buff.readChar(128 + 32)
    buff.readChar(10)
    buff.readChar(5)
    buff.readChar(b'c')
    buff.readChar(b'i')
    buff.readChar(b'a')
    buff.readChar(b'o')
    buff.readChar(0)

    if buff.readChar(b'\xfe'):
        print(buff.toString())

    buff.setDeviceId(10)

    print(buff.toString())
