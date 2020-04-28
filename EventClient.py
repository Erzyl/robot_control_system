#!/usr/bin/env python3

import socket
import sys


class EventClient:


    def __init__(self):
        self.host = '127.0.0.1'  # The server's hostname or IP address
        self.port = 65432        # The port used by the server

    def connect(self, input):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(bytes(input, 'ascii')) # Send message to all
            data = s.recv(1024) # Recieve data from server

        print('Received: ', repr(data.decode("ASCII")))


if __name__ == "__main__":
    EventClient().connect(sys.argv[1])