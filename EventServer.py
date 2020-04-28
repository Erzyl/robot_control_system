#!/usr/bin/env python3

import socket
import threading
import time

class EventServer:

    def __init__(self,ip = '127.0.0.1',port = 65432):
        self.host = ip
        self.port = port  
        self.Running = True
        self.main_list = []

    def run_server(self):
        # Adress family - IPv4; Socket type - TCP;
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # To force socket rebindin
            s.bind((self.host, self.port)) # Associate socket with specific network interface nad port
            s.listen() # Enables server to accept connections / Makes it a listening socket
            print('Server Started')

            x = threading.Thread(target=self.get_input, args=('Message',))
            x.start()
            while self.Running:
                
                conn, addr = s.accept() # New connection creates new s. Touple (ip,port)
                with conn: # With the new connection
                    #print('New client connected by', addr) # Initial message
                    data = conn.recv(1024) # Reads what client sends
                    data_decoded = data.decode("ASCII")
                    print('New entry: {0} by {1}'.format(data_decoded,addr))
                    self.main_list.append(data_decoded)
                    conn.sendall(data) # Sends data to all connections
            
        s.close()

    def get_input(self,s):
        while True:
            s = input()
            #time.sleep(2)
            if "list" in s:
                print(self.main_list)

if __name__ == "__main__":
    e = EventServer("127.0.0.1",65432)
    e.run_server()