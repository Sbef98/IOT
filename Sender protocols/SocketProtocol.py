from socket import socket


def newBuffer():
    return {"id": -1,
            "initialized": False,
            "inBuffer": None,
            "outBuffer": None
            }


class SocketCom:
    """
    SocketCom is the single socket communication
    """
    @staticmethod
    def getIstance(remoteServer, port, isActuator=False, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        s = SocketCom(remoteServer, port, beginTrigger, endTrigger)
        s.outBuffer.setActuatorFlag(isActuator)
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
        self.buffers = [self.buffers]   # turning the previously single istance into a list


class SocketFactory:
    """
    """
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
