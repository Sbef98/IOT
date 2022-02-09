import socket

from bridge.handler import createProtocolMessage

BRIDGE = '127.0.0.1'
PORT = '65432'

socket_connection_number = 0


def sendToBridge(deviceid, person, gender, age):
    datasize = 0
    person = person % 255  # we do not expect to have more than 255 people in one shop at the same time
    message = createProtocolMessage(
        flags=0,
        device_id=deviceid,
        datasize=datasize,
        data=['id', person, 'g', gender, 'a', age])
    sendViaSocket(message)


def sendViaSocket(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((BRIDGE, int(PORT)))
        s.sendall(message)
        data = s.recv(1024)

    print('Received', repr(data))
