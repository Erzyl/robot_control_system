#!/usr/bin/env python3

import socket
import sys
import pickle


class EventClient:

    def __init__(self):
        self.host = '127.0.0.1'  # The server's hostname or IP address
        self.port = 65432        # The port used by the server


    def connect(self, input):

        # Specific input for singla command at to current protocol
        with open(input) as f:
            self.protocol = f.read().splitlines()


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))

            data = pickle.dumps(self.protocol)
            s.send(data)
            data_recivied = s.recv(1024) # Recieve data from server

        print(data_recivied.decode("ascii"))


if __name__ == "__main__":
    EventClient().connect(sys.argv[1])