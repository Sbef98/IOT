from typing import Protocol
import protocol


class SocketCom:
    """
    SocketCom is the single socket communication 
    """
    def __init__(self, remoteServer, port, beginTrigger=b'\xff', endTrigger=b'\xfe'):
        inBuffer = Protocol(beginTrigger, endTrigger)


class ControllerFactory:
    """
    It's our "Controller loop" in sockets.
    It may be useful having a controller loop for the socket
    communication too so that we can create SocketComs like a
    factory pattern.
    Why doing so?
    If we need an high-throughput, we can 
    """

    def __init__(self, remoteServer, portRange=[8000, 9000]):
        """
            portRange is useful in case i want to decide on which ports
            range i want my sockets to work on!
        """
        pass
