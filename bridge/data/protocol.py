import types

def emptyProtocolInBuffer():
    return types.SimpleNamespace(data = [], flags = -1, device_id = -1, self.data_length = 0)

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
    def __init__(self):
        self.inBuffer = emptyProtocolInBuffer()

    def addValue(self, val):
	if (val == b'\xfe'): #EOL
            return True

        elif (val == b'\xff'):
            self.inBuffer = emptyProtocolInBuffer()

        else:
            if(self.inBuffer.flags == -1):
                self.inBuffer.flags = val
            elif(self.inBuffer.device_id == -1):
                self.inBuffer.device_id = val
            else:
                self.inBuffer.data.append(val)
                self.inBuffer.data_length += 1

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

