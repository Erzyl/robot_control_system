#!/usr/bin/env python3

import socket
import threading
import time
import pickle
import re

from Plate import Plate
from RoboConnect import RoboConnect
from BuildProtocol import BuildProtocol
from RoboRun import RoboRun


class EventServer:

    def __init__(self,ip = '127.0.0.1',port = 65432):
        self.host = ip
        self.port = port  
        self.Running = True
        self.plate_list = []

        self.current_global_position = "h_checkPoint10"
        self.build_checkpoints = BuildProtocol()
        self.robot_connection = RoboConnect()
        self.robot_run = RoboRun()

    def run_server(self):


        # Start connection to robot server     
        self.robot_connection.connect()
    
        
         # Thread: Get key inputs
        key_input_manager = threading.Thread(target=self.get_input, args=('Message',))
        key_input_manager.start()

        # Thread: Get new plate inputs, protocol files or single commmands
        input_server = threading.Thread(target=self.plate_list)
        input_server.start()

        # Thread: Run system
        input_server = threading.Thread(target=self.system_runner)
        input_server.start()



    def system_runner(self):
        #go_next = 0
        while True:
            #go_next = go_next + 0.01 if go_next < 1 else 1

            #if go_next == 1:
                #go_next = 0
            # Add threading here for overlapping movment
            self.move_next()

    # When reached target, change current to dest and move on etc.
    
    def move_next(self): # Do the next moves
        move_from = self.current_global_position
        plateToMove = self.priority_system()
        move_to = self.plate_list[plateToMove]
        movment = [move_from,move_to]
        # Get list with all the check points from current pos to target pos
        movement_with_cp = self.build_checkpoints.build_protocol(movment)
        # Run system between the 2 steps including checkpoints
        self.robot_run.start(self.robot_connection.tn, movement_with_cp)

        self.current_global_position = move_to



    def priority_system(self): # Get the next moves
        cur_move = 0
        self.plate_list[cur_move].step()

        return 0 # Return plate that should be moved


    def plate_inputs(self):
        # Adress family - IPv4; Socket type - TCP;
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # To force socket rebindin
            s.bind((self.host, self.port)) # Associate socket with specific network interface nad port
            s.listen() # Enables server to accept connections / Makes it a listening socket
            print('Server Started')


            while self.Running:
                
                conn, addr = s.accept() # New connection creates new s. Touple (ip,port)
                with conn: # With the new connection

                    # Add event to current plate
                    #data_decoded = data.decode("ASCII")
                    #print('New entry: {0} by {1}'.format(data_decoded,addr))
                    #self.main_list.append(data_decoded)

                    # Add new plate
                    print('New entry by', addr) 
                    data = pickle.loads(conn.recv(4096)) # Reads what client sends
                    plate_number = len(self.plate_list)+1
                    newPlate = Plate(plate_number,data)
                    self.plate_list.append(newPlate)             
                    for x in data:
                        print(x)
 
                    conn.send(bytes("Entry successfully added!","ascii"))         
        #s.close()


    def get_input(self,s):
        while True:
            s = input()
            time.sleep(0.5)
            if "plate" in s:
                if self.is_num(s):
                    num = int(s[len(s)-1])
                    if len(self.plate_list) >= num:
                        self.get_plate_info(num)
                    else:
                        print("Plate not found")

    
    def get_plate_info(self,plate_num):
        plate = self.plate_list[plate_num-1]
        print("Plate number {0}, status:".format(plate.id))
        print("Current position: {0}".format(plate.current))
        print("Destination: {0}".format(plate.destination))

    def is_num(self,string):
        return any(i.isdigit() for i in string)


if __name__ == "__main__":
    e = EventServer("127.0.0.1",65432)
    e.run_server()