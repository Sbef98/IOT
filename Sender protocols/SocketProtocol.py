from copyreg import pickle
from socket import socket
from threading import Thread

from bridge.data.protocol import ProtocolBuffer


def newBuffer():
    return {"id": -1,
            "initialized": False,
            "inBuffer": None,
            "outBuffer": None,
            "isActuator": False,
            "packetNumber": 0,
            "inPacketFull": False,
            "outPacketFull": False,
            }



class SocketCom:
    """
    SocketCom abstract
    """
    @staticmethod
    def getIstance(remoteServer, port, isActuator=False, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        pass
    @staticmethod
    def connectToHost(remoteServer, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCKET_STREAM)
        except socket.error:
            print("Failed to create socket")
            return None

        s.connect((remoteServer, port))
        return s

    def __init__(self, remoteServer, port, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        self.beginTrigger = beginTrigger
        self.endTrigger = endTrigger
        self.s = SocketCom.connectToHost(remoteServer, port)
        self.alive = True
        self.buffers = None  # Single object for single socket, list for multi one
    
    def sendData(self, data, device_id):
        pass
    
    def readNewData(self, device_id):
        pass

    def initializeDevice(self, device_id, dataType):
        pass

    def addDataToBuff(self, buff, value):
        buff.addValue(value)
        return buff
    
    def addDatasToBuff(self, buff, values):
        for value in values:
            buff.addValue(value)
        return buff

    def sendMessage(self, buff, values):
        buff = addDatasToBuff(buff, values)

        correct, excep = buff.isMessageCorrect()
        if not correct:
            raise Exception(excep)

        self.s.send(chr(buff.beginTrigger))
        self.s.send(chr(buff.getFlags()))
        self.s(chr(buff.getDeviceId()))
        self.s.send(chr(buff.getDataSize()))
        
        for data in buff:
            self.s.send(chr(d))

        self.s.sendall(chr(buff.endTrigger))

    def sendInitializationMessage(self, buff, string):
        if not buff.isInitializationMessage():
            buff.setInitializationFlag(True)

        self.sendData(buff, string)

    def readMessage(self):
        buff = emptyProtocolInBuffer()
        while True:
            recv_data = self.s.recv(1)
            if recv_data:
                reading_done = buff.readChar(recv_data)
                if reading_done:
                    return buff

    def readInitializationMessage(self):
        buff = self.readMessage()
        if not buff.isInitializationMessage():
            print ("Data received before getting initialization message")
            return buff, False

        return buff, True
    
    def isDataAvailable(self):
        """
        I do not know yet
        """
        pass





class AsyncSocketCom(SocketCom):
    """
    The difference in this subclass it is that we will be using a singleton.
    This means we will always return the same istance.
    Ofc, it will be slightly changed from the previous one.
    For example, getting an instance will always return the same object (it's a singleton...)
    But in this case we will add a new buffer for each new device
    """
    __instance = None

    @staticmethod
    def getIstance(remoteServer, port, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        if AsyncSocketCom.__instance is None:
            AsyncSocketCom(remoteServer, port, beginTrigger, endTrigger)
        else:
            newId = AsyncSocketCom.__instance.addNewBuffer()

        return AsyncSocketCom.__instance, newId

    def addNewBuffer(self):
        nb = newBuffer()

        if len(self.buffers) != 0 and not self.buffers[-1]["initialized"]:
            nb["id"] = self.buffers[-1]["id"] - 1

        self.buffers.append(newBuffer)

        return nb["id"]

    def __init__(self, remoteServer, port, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        super().__init__(remoteServer, port, beginTrigger, endTrigger)
        self.buffers = [ newBuffer(), ]

        self.t = Thread(target= self.continuousReading(), daemon=True)  # Not gonna block
        self.t.start()
        
    
    def continuousReading(self):
        while True:
            buff = self.readMessage()
            targetPacket = None    # allows me to know if i found the device among the listed ones
            packet_in_saved = False

            # This for is to save the message read and as long as it is running it also sends all the packets not sent yet
            for packet in self.buffers:
                if packet['id'] == buff.getDeviceId and not packet_saved:
                    device_found = True
                    if not device["inPacketFull"]:
                        packet["inBuffer"] = buff
                        packet["inPacketFull"] = True
                        packet_saved = True
                    else:
                        targetPacket = packet
                
                if packet["outPacketFull"]:
                    if packet["outBuffer"].isInitializationMessage():
                        self.sendInitializationMessage(packet["outBuffer"], packet["outBuffer"].getDataAsList())  # Needs some optimization indeed
                    else:
                        self.sendMessage(packet["outBuffer"], packet["outBuffer"].getDataAsList())
                    packet["outPacketFull"] = False
                    if not packet["inPacketFull"] and not packet["packetNumber"] == 0: # If this is not the basic device buffer and is fully empty
                        self.buffers.remove(packet)
            
            if targetPacket and not packet_saved:
                new_packet = newBuffer()
                new_packet["id"] = targetPacket["id"]
                new_packet['isActuator'] = targetPacket["isActuator"]
                new_packet["initialized"] = targetPacket["initialized"]
                new_packet["packetNumber"] = targetPacket["packetNumber"] + 1
                new_packet["inBuffer"] = targetPacket["inBuffer"]
                new_packet["inPacketFull"] = True
                new_packet["inBuffer"].setDeviceId(device_id)
                new_packet["inBuffer"] = emptyProtocolInBuffer()
                new_packet["inBuffer"].setActuatorFlag(packet["isActuator"])

        
    def sendData(self, data, device_id):

        targetPacket = None    # allows me to know if i found the device among the listed ones

        for packet in self.buffers:
            if(packet['id'] == device_id):

                if not packet["initialized"]:
                    raise Exception("Cannot send data from not initialized device")

                if(device["outPacketFull"]) == True:
                    targetPacket = packet
                    continue
            
                packet["outBuffer"] = emptyProtocolInBuffer()
                packet["outBuffer"].setDeviceId(device_id)
                packet["outBuffer"].setActuatorFlag(packet["isActuator"])
                packet["outPacketFull"] = True

                return
            
        if targetPacket:
            new_packet = newBuffer()
            new_packet["id"] = targetPacket["id"]
            new_packet['isActuator'] = targetPacket["isActuator"]
            new_packet["packetNumber"] = targetPacket["packetNumber"] + 1
            new_packet["initialized"] = targetPacket["initialized"]
            new_packet["outBuffer"].setDeviceId(device_id)
            new_packet["outBuffer"] = emptyProtocolInBuffer()
            new_packet["outBuffer"].setActuatorFlag(packet["isActuator"])

            new_packet["outPacketFull"] = True
            
        else:
            raise Exception("Wrong socket for this device")  # If no buffer for this device
            

    def readNewData(self, device_id):
        no_device_with_id = True
        is_initialization_message = False
        data = []

        for packet in self.buffers:

            if(packet['id'] == device_id):
                no_device_with_id = False

                if not packet["initialized"]:
                    raise Exception("Cannot read data for not initialized device")

                if packet["inPacketFull"]:
                    data.append(packet["inBuffer"])
                    is_initialization_message = packet["inBuffer"].isInitializationMessage()

                    packet["inPacketFull"] = False
                    if not packet["outPacketFull"] and not packet["packetNumber"] == 0:
                        self.buffers.remove(packet)
        
        if no_device_with_id:
            raise Exception("Wrong socket for this device")  # If no buffer for this device

        return data, device_id, is_initialization_message

    def initializeDevice(self, device_id, dataType):

        for packet in self.buffers:
            if(packet["id"] == device_id):
                packet["outBuffer"] = emptyProtocolInBuffer()
                packet["outBuffer"].setDeviceId(device_id)
                packet["outBuffer"].setActuatorFlag(self.buffers["isActuator"])
                
                if not packet["outBuffer"].isInitializationMessage():
                    buff.setInitializationFlag(True)
                
                self.sendData(dataType, device_id)

                data, device_id, is_initialization_message = self.readNewData(device_id)

                if is_initialization_message:
                    packet["id"] = device_id
                    packet["initialized"] = True
                    return data
                break

class SingleSocketCom(SocketCom):
    """
    SocketCom is the single socket communication
    """
    @staticmethod
    def getIstance(remoteServer, port, isActuator=False, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        s = SocketCom(remoteServer, port, beginTrigger, endTrigger)
        s.buffers["isActuator"] = isActuator
        return s, -1

    def connectToHost(self, remoteServer, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCKET_STREAM)
        except socket.error:
            print("Failed to create socket")
            return None

        s.connect((remoteServer, port))
        return s

    def __init__(self, remoteServer, port, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        self.beginTrigger = beginTrigger
        self.endTrigger = endTrigger
        self.s = self.connectToHost(remoteServer, port)
        self.alive = True
        self.buffers = newBuffer()
    
    def sendData(self, data, device_id):

        # types.SimpleNamespace(data=[], flags=-1, sent_data_size=None, device_id=-1, data_length=0)

        if not self.buffers["id"] == device_id:
            raise Exception("Wrong socket for this device")
        if not self.buffers["initialized"]:
            raise Exception("Cannot send data from not initialized device")
        
        self.buffers["outBuffer"] = emptyProtocolInBuffer()
        self.buffers["outBuffer"].setDeviceId(device_id)
        self.buffers["outBuffer"].setActuatorFlag()

        self.sendMessage(self.buffers["outBuffer"], data)
    
    def readNewData(self, device_id):
        if not self.buffers["id"] == device_id:
            raise Exception("Wrong socket for this device")
        if not self.buffers["initialized"]:
            raise Exception("Cannot read data for not initialized device")
        self.buffers["inBuffer"] = self.readMessage()
        return self.buffers["inBuffer"].getDataAsList()

    def initializeDevice(self, device_id, dataType):
        if not self.buffers["id"] == device_id:
            raise Exception("Wrong socket for this device")
        
        self.buffers["outBuffer"] = emptyProtocolInBuffer()
        self.buffers["outBuffer"].setDeviceId(device_id)
        self.buffers["outBuffer"].setActuatorFlag(self.buffers["isActuator"])

        self.sendInitializationMessage(self.buffers["outBuffer"], dataType)

        self.buffers["inBuffer"], correct_initialization = self.readInitializationMessage()
        if correct_initialization:
            self.buffers["id"] = self.buffers["inBuffer"].getDeviceId()
            self.buffers["initialized"] = True

        


class SocketFactory:

    def garbageCollector(self):
        """
        Will use this to clean the broken connections
        or the inactive ones.
        Eventually, will try to revive them or just deleting them out.
        The deactivated connections' port will be available for new connections
        in the inactivePorts list
        """
        for port in range(self.portRange[0], self.nextActivePort):
            pass

    def __init__(self, remoteServer, portRange=[8000, 9000]):
        self.portRange = portRange
        # The first port in the porta range will be kept for an eventual async Socket
        self.nextActivePort = portRange[0] + 1
        self.inactivePorts = []

    def initSocket(self, multiMode = True, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        """
        Returns a SocketCom either way.
        The AsyncSocketCome is a SocketCom subclass anyway!
        """
        if multiMode:
            AsyncSocketCom.getIstance(self.remoteServer, self.portRange[0], beginTrigger, endTrigger)
        if not multiMode:
            SocketCom.getIstance(self.remoteServer, self.portRange[0], beginTrigger, endTrigger)


if __name__ == "__main__":
    pass