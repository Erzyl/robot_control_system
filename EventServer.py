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
        self.lid_spots = [-1]*3
        self.hotel_spots = [0]*14

        self.current_global_position = "h_get"
        self.build_checkpoints = BuildProtocol()
        self.robot_connection = RoboConnect()
        self.robot_run = RoboRun()

        self.connect_to_robot = False

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

        # Thread: Run system
        input_server = threading.Thread(target=self.system_runner)
        input_server.start()



    def system_runner(self):
        #go_next = 0

        while True:
            #go_next = go_next + 0.01 if go_next < 1 else 1


            if len(self.plate_list) == 0 or not self.connect_to_robot:
                time.sleep(2)
                continue
            # Add threading here for overlapping movment
            self.move_next()

    # When reached target, change current to dest and move on etc.

    def move_next(self): # Do the next moves
        move_from = self.current_global_position
        plateToMove = self.plate_list[self.priority_system()]
        move_to = plateToMove.path[plateToMove.curStep]
        movment = [move_from,move_to]
        self.plate_list[self.priority_system()].step()
        # Get list with all the check points from current pos to target pos
        movement_with_cp = self.build_checkpoints.build_protocol(movment,id,plateToMove)
        # Run system between the 2 steps including checkpoints
        self.robot_run.start(self.robot_connection.tn, movement_with_cp,id,plateToMove)

        self.current_global_position = move_to



    def priority_system(self): # Get the next moves

        for plate in self.plate_list: ## Currently prioritises plates added in order
            cur_step = plate.path[plate.curStep]
            if self.build_checkpoints.w_get in cur_step:
                if self.robot_run.is_washer_ready(): # Set a min time for readines
                    return plate.id
                else:
                    continue
            elif self.build_checkpoints.d_get in cur_step:
                if self.robot_run.is_dispenser_ready(): # Set a min time for readines
                    return plate.id
                else:
                    continue
            elif self.build_checkpoints.s_get in cur_step:
                if self.robot_run.is_shaker_ready(): # Set a min time for readines
                    return plate.id
                else:
                    continue
            elif self.build_checkpoints.hp in cur_step: # Return plate to hotel
                # Reservs a hotel spot before returning plate to hotel
                fs = self.get_free_hotel_spot()
                if fs != -1:
                    self.hotel_spots[fs] = plate.id
                    return plate.id
                else:
                    continue # Should not work in case robot is already holding a plate
            elif self.build_checkpoints.hg in cur_step: # Get plate from hotel
                # Reserv lid spot
                fs = self.get_free_lid_spot()
                if fs != -1:
                    self.lid_spots[fs] = plate.id # Add lid spots directly to plate object?
                    return plate.id
                else:
                    continue # Should not work in case robot is already holding a plate
            else: # If last spot was not to a device
                return plate.id

        # if plate has no more paths, add h_put to free spot

        return -1


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
                    h_spot = re.findall(r'[0-100]',data[0])
                    self.hotel_spots[0] = plate_number

                    newPlate = Plate(plate_number,data)

                    self.plate_list.append(newPlate)
                    print('Current amount of plates: ' +str(len(self.plate_list)))
                    # for x in data:
                    #     print(x)

                    conn.send(bytes("Entry successfully added!","ascii"))
        s.close()


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
            if "get plates" in s:
                self.get_plates_in_system()


    def get_plates_in_system(self):
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


    def get_free_lid_spot(self):
        index = 0
        for x in self.lid_spots:
            if x == -1:
                return index
        return -1

    def get_lid_spot(self,plate_id):
        try:
            return self.lid_spots.index(plate_id)
        except ValueError:
            return -1

    def get_free_hotel_spot(self):
        index = 0
        for x in self.hotel_spots:
            if x == -1:
                return index
        return -1

    def get_hotel_spot(self,plate_id):
        try:
            return self.lid_spots.index(plate_id)
        except ValueError:
            return -1


if __name__ == "__main__":
    e = EventServer("127.0.0.1",65432)
    e.run_server()
