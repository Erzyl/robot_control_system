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
from Prioritizer import Prioritizer


class EventServer:

    def __init__(self,ip = '127.0.0.1',port = 65432):
        self.host = ip
        self.port = port
        self.Running = True # Run robot and devices

        self.plate_list = []
        self.lid_spots = [-1]*3
        self.hotel_spots = [0]*14

        self.current_global_position = "h_get"
        self.build_checkpoints = BuildProtocol()
        self.robot_connection = RoboConnect()
        self.robot_run = RoboRun()
        self.prioritizer = Prioritizer()

        self.connect_to_robot = True # For debugging without connecting to robot


    def run_server(self):

        # Start connection to robot server
        if self.connect_to_robot:
            self.robot_connection.connect()

         # Thread: Get key inputs
        key_input_manager = threading.Thread(target=self.get_input, args=('Message',))
        key_input_manager.start()

        # Thread: Get new plate inputs, protocol files or single commmands
        input_server = threading.Thread(target=self.plate_inputs)
        input_server.start()

        # Thread: Run robot and device system
        input_server = threading.Thread(target=self.system_runner)
        input_server.start()


    def system_runner(self):

        while True:

            if len(self.plate_list) == 0:
                time.sleep(2)
                continue

            # Add threading here for overlapping movment
            self.move_next()


    # When reached target, change current to dest and move on etc.
    def move_next(self): # Do the next moves
        move_from = self.current_global_position
        plateToMove = self.prioritizer.get_prio_plate(self.plate_list,self.hotel_spots,self.lid_spots)
        move_to = plateToMove.path[plateToMove.cur_step]
        movment = [move_from,move_to]

        data_list = [self.hotel_spots,self.lid_spots]
        movement_with_cp = self.build_checkpoints.build_protocol(movment,plateToMove.id, data_list)

        # Run system between the 2 steps including checkpoints
        if self.connect_to_robot:
            updated_lists = self.robot_run.start(self.robot_connection.tn, movement_with_cp,data_list,plateToMove) # Holds this thread until run is done, might want to split

            self.hotel_spots = updated_lists[0]
            self.lid_spots = updated_lists[1]

            self.current_global_position = move_to
            self.plate_list[self.get_plate_list_index(plateToMove)].step() # Advance plate to next step in path
            
        else: 
            time.sleep(20)


    def plate_inputs(self):
        # Adress family - IPv4; Socket type - TCP;
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # To force socket rebindin
            s.bind((self.host, self.port)) # Associate socket with specific network interface nad port
            s.listen() # Enables server to accept connections / Makes it a listening socket
            print('Protocol server started successfully!')


            while self.Running:

                conn, addr = s.accept() # New connection creates new s. Touple (ip,port)
                with conn: # With the new connection

                    # Add new plate
                    print('New entry by', addr)
                    data = pickle.loads(conn.recv(4096)) # Reads what client sends
                    plate_number = len(self.plate_list)+1

                    h_spot = re.findall(r'[0-9]+',data[0])

                    self.hotel_spots[int(h_spot[0])-1] = plate_number

                    newPlate = Plate(plate_number,data)

                    self.plate_list.append(newPlate)
                    print('Current amount of plates: ' +str(len(self.plate_list)))

                    conn.send(bytes("Entry successfully added!","ascii"))
        #s.close()


    ### CHECK INPUTS ###
    def get_input(self,s):
        while True:
            s = input()
            time.sleep(0.5)

            if "plate" in s:
                if self.is_num(s):
                    num = int(s[len(s)-1])
                    if len(self.plate_list) >= num:
                        self.get_plate_info(num-1)
                    else:
                        print("Plate not found")
            elif "check plates" in s:
                self.check_plates()

            elif "check hotel" in s:
                self.check_hotel()
            elif "check lid" in s:
                self.check_lid()


    def check_hotel(self):
        i = 0
        for cur_spot in self.hotel_spots:
            if cur_spot == 0:
                check = "empty"
            else:
                check = "{Plate id: " +str(cur_spot) + "}"

            print("Hotel spot " + str(i+1) + ": " + check)
            i += 1


    def check_lid(self):
        i = 0
        for cur_spot in self.lid_spots:
            if cur_spot == -1:
                check = "empty"
            else:
                check = "{Plate id: " +str(cur_spot) + "}"
            print("Lid spot " + str(i+1) + ": " + check)
            i += 1


    def check_plates(self):
        for cur_plate in self.plate_list:
            print("Plate id: " + str(cur_plate.id))


    def get_plate_info(self,plate_num):
        plate = self.plate_list[plate_num]
        print("Plate id: {0}, status:".format(plate.id))
        print("Current position: {0}".format(plate.path[plate.cur_step]))
        # Check if not at last
        print("Destination: {0}".format(plate.path[plate.cur_step+1]))

    def is_num(self,string):
        return any(i.isdigit() for i in string)


    ### Get spots ###
    def get_plate_list_index(self,id):
        i = 0
        for p in self.plate_list:
            if p.id == id:
                return i
            i+=1


    def get_list_spot(self,plate_id,lista):
        try:
            return lista.index(plate_id)
        except ValueError:
            return -1




if __name__ == "__main__":
    e = EventServer("127.0.0.1",65432)
    e.run_server()
