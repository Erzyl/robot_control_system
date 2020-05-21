#!/usr/bin/env python3
import telnetlib
import time
import requests
from BuildProtocol import BuildProtocol

class RoboRun:

    DEFAULT_PATH = "/programs/FINAL/"
    WASHER_PATH = "http://washer.lab.pharmb.io:5000/execute_protocol/"
    DISPENSER_PATH = "http://dispenser.lab.pharmb.io:5001/execute_protocol/"
    SHAKER_PATH = ""

    def __init__(self):
        self.tn = -1
        self.pd = BuildProtocol()

    def start(self, telnet_connection, protocol, data_list, plate_id):
        self.tn = telnet_connection
        self.protocol = protocol
        self.hotel_spots = data_list[0]
        self.lid_spots = data_list[1]
        self.plate_id = plate_id

        self.run()
        
        data = [self.hotel_spots,self.lid_spots]
        return data

    def run(self):

        # Handle protective stop
        # self.tn.write(b"safetystatus\n")
        # status = self.read_last()
        # if status == "PROTECTIVE_STOP":
        #     self.tn.write(b"unlock protective stop\n")

        # Execute
        for c in self.protocol:
            self.execute_protocol(c)

        # Stop
        #self.tn.write(b"quit\n")


    def execute_protocol(self, program):

        if self.pd.washer_play in program:
            self.play_washer(program)
        elif self.pd.dispenser_play in program:
            self.play_dispenser(program)
        elif self.pd.shaker_play in program:
            self.play_shaker(program)
        # elif program == self.pd.washer_wait:
        #     while (not self.is_washer_ready()):
        #         time.sleep(1)
        # elif program == self.pd.dispenser_wait:
        #     while (not self.is_dispenser_ready()):
        #         time.sleep(1)
        # elif program == self.pd.shaker_wait:
        #     while (not self.is_shaker_ready()):
        #         time.sleep(1)
        else:
            print("Loading: "+program)
            prog = "load " + self.DEFAULT_PATH + program + ".urp\n"
            self.tn.write(bytes(prog, 'ascii'))
            time.sleep(1)
            self.tn.write(b"play\n")
            time.sleep(1)

            has_played = False
            #self.get_run_status()
            while self.get_run_status() == "Program running: true\n": # Freeze roboRunner if arm is being used
                print("PLAYING")
                time.sleep(1)
                has_played = True

            # Free up lid spot after puting lid back on the plate
            if program in self.pd.sw_lidOn:
                spot = self.get_list_spot(self.plate_id,self.lid_spots)
                self.lid_spots[spot] = -1

            # Free up hotel spot after taking the plate from the hotel
            if program in self.pd.hg:
                spot = self.get_list_spot(self.plate_id,self.lid_spots)
                self.hotel_spots[spot] = -1

            if has_played:
                print("Finished: " + program)
            else:
                print("Failed: " + program)


    def get_list_spot(self,plate_id,lista):
        try:
            return lista.index(plate_id)
        except ValueError:
            return -1

    def play_washer(self, protocol):
        time.sleep(1) # Give the arm time to move out of the way
        while (not self.is_washer_ready()):
            time.sleep(1)
            print("Waiting for washer to get ready")
        print("Starting Washer")
        p1, p2 = protocol.rsplit(": ")
        requests.get(self.WASHER_PATH + p2)

    def play_dispenser(self, protocol):
        time.sleep(1) # Give the arm time to move out of the way
        while (not self.is_dispenser_ready()):
            time.sleep(1)
            print("Waiting for dispenser to get ready")
        print("Starting dispenser")
        p1, p2 = protocol.rsplit(": ")
        requests.get(self.DISPENSER_PATH + p2)

    def play_shaker(self, protocol):
        time.sleep(1) # Give the arm time to move out of the way
        while (not self.is_shaker_ready()):
            time.sleep(1)
            print("Waiting for shaker to get ready")
        print("Starting shaker")
        p1, p2 = protocol.rsplit(": ")
        requests.get(self.SHAKER_PATH + p2)


    def is_dispenser_ready(self):
        r = requests.get('http://dispenser.lab.pharmb.io:5001/is_ready')
        r_dict = r.json()
        if str(r_dict['value']) == "True":
            print("Dispenser is ready")
            return True
        else:
            print("Dispenser is not ready")
            return False

    def is_washer_ready(self):
        r = requests.get('http://washer.lab.pharmb.io:5000/is_ready')
        r_dict = r.json()
        if str(r_dict['value']) == "True":
            print("Washer is ready")
            return True
        else:
            print("Washer is not ready")
            return False

    def is_shaker_ready(self):
        r = requests.get('http://shaker.lab.pharmb.io:5000/is_ready')
        r_dict = r.json()
        if str(r_dict['value']) == "True":
            print("Shaker is ready")
            return True
        else:
            print("Shaker is not ready")
            return False


    def read_last(self):
        #buffer = self.tn.read_eager().decode('ascii')
        buffer = self.tn.read_very_eager().decode('ascii')
        print(buffer)
        return buffer


    def get_run_status(self):
        junk = self.tn.read_very_eager()
        self.tn.write(b"running\n")
        time.sleep(1)
        status = self.read_last()
        #print("Run status: " + status)
        return status
