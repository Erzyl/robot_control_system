#!/usr/bin/env python3
import telnetlib
import time
import requests


class RoboTelnet:

    HOST = "130.238.44.58"
    PORT = 29999
    DEFAULT_PATH = "/programs/FINAL/"

    def __init__(self):
        self.tn = -1
        self.protocol = []


    def start(self):
        self.connect_telnet()
        self.build_protocol()
        self.run()


    def connect_telnet(self):
        self.tn = telnetlib.Telnet(self.HOST, self.PORT)
        self.tn.read_until(b"Dashboard Server")
        # self.tn.write(b"robotmode\n")
        # time.sleep(1)
        # self.read_last()


    def build_protocol(self):

        # INITIATE
        h_get = []
        h_put = []
        for i in range(18):
            h_get.append("h" + str(i + 1) + "_get")
            h_put.append("h" + str(i + 1) + "_put")

        # washer
        w_get = "sw_washerGet"
        w_put = "sw_washerPut"

        # dispenser
        d_get = "d_get"
        d_put = "d_putH"

        # shaker
        s_get = -1
        s_put = -1

        washer_play = "washer"
        dispenser_play = "dispenser"

        # misc checkpoints - Should not be entered by the user
        h_checkPoint = "h_checkPoint10" # when going between hotel spots # > 10
        h_to_sw = "h_to_sw" # hotel to switch
        sw_to_h = "sw_to_h" # switch to hel
        sw_to_washHigh = "sw_to_washHigh" # switch to above washer
        washHigh_to_sw = "washHigh_to_sw" # above washer to switch
        w_above = "w_above" # wait above washer
        gripper_open = "griperOpen" # force open grippers
        horToVer = "sw_safe_horToVer" # in sw, switch horizontal grip to vertical
        verToHor = "sw_safe_verToHor" # switch vertical to horizontal grip

        sw_safeHor = "sw_safeHor"
        sw_getHor = "sw_getHor"
        sw_putHor = "sw_putHor"
        sw_putHorHigh = "sw_putHorHigh"

        sw_safeVer = "sw_safeVer"
        sw_getVer = "sw_getVer"
        sw_putVer = "sw_putVer"

        sw_lidOff = "sw_lidOff"
        sw_lidOn = "sw_lidOn"

        washer_wait = "washer_wait"
        dispenser_wait = "dispenser_wait"

        def ap(protocol):
            self.protocol.append(protocol)

        # SET PROTOCOL

        ### HOTEL TO SW ###
        ap(h_get[14])
        ap(h_to_sw)
        ap(sw_putHor)
        ap(sw_lidOff)

        ### SW TO Washer ###
        ap(sw_to_washHigh)
        ap(w_put)
        ap(washer_play)
        ap(washHigh_to_sw)

        ### SW TO HOTEL ###
        ap(sw_to_h)
        ap(h_get[16]) # 17
        ap(h_to_sw)
        ap(sw_putHor)

        ### SW TO DISPENSER ###
        ap(gripper_open)
        ap(horToVer)
        ap(sw_getVer)
        ap(d_put)
        ap(dispenser_play)

        # Get plate from washer to hotel - From SW_ver
        ap(verToHor)
        ap(sw_to_washHigh)
        ap(w_get)
        ap(washHigh_to_sw)
        ap(sw_putHorHigh)
        ap(sw_getHor)
        ap(sw_to_h)
        ap(h_put[17])

        # Get plate from dispenser to hotel - From hotel
        ap(h_to_sw)
        ap(horToVer)
        ap(d_get)
        ap(sw_putVer)
        ap(verToHor)
        ap(sw_getHor)
        ap(sw_to_h)
        ap(h_checkPoint)
        ap(h_put[0])

        # Get postWasher plate to disp
        ap(h_checkPoint)
        ap(h_get[17])
        ap(h_to_sw)
        ap(sw_putHor)
        ap(horToVer)
        ap(sw_getVer)
        ap(d_put) # Might need to be putH ?
        ap(dispenser_play)
        ap(dispenser_wait)
        ap(d_get)
        ap(sw_putVer)
        ap(verToHor)
        ap(sw_getHor)
        ap(sw_to_h)
        ap(h_put[17])


        # RANDOM TEST
        # ap(sw_putVer)
        # ap(verToHor)
        # ap(sw_to_h)




    def play_washer(self):
        time.sleep(1) # Give the arm time to move out of the way
        while (not self.is_washer_ready()):
            time.sleep(1)
            print("Waiting for washer to get ready")
        print("Starting Washer")
        requests.get('http://washer.lab.pharmb.io:5000/execute_protocol/demo/2_W_wash_80uL_A.LHC')

    def play_dispenser(self):
        time.sleep(1) # Give the arm time to move out of the way
        while (not self.is_dispenser_ready()):
            time.sleep(1)
            print("Waiting for dispenser to get ready")
        print("Starting dispenser")
        requests.get('http://dispenser.lab.pharmb.io:5001/execute_protocol/demo/3_D_dispense_60uL_PFA_Sa.LHC')

    def is_dispenser_ready(self):
        r = requests.get('http://dispenser.lab.pharmb.io:5001/is_ready')
        r_dict = r.json()
        if str(r_dict['value']) == "True":
            print("Disp is ready")
            return True
        else:
            print("Disp is not ready")
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
        self.tn.write(b"quit\n")


    def execute_protocol(self, program):

        if program == "washer":
            self.play_washer()
        elif program == "dispenser":
            self.play_dispenser()
        elif program == "washer_wait":
            while (not self.is_washer_ready()):
                time.sleep(1)
        elif program == "dispenser_wait":
            while (not self.is_dispenser_ready()):
                time.sleep(1)
        else:
            print("Attempting: "+program)
            prog = "load " + self.DEFAULT_PATH + program + ".urp\n"
            self.tn.write(bytes(prog, 'ascii'))
            time.sleep(1)
            self.tn.write(b"play\n")
            time.sleep(1)

            has_played = False
            #self.get_run_status()
            while self.get_run_status() == "Program running: true\n":
                print("PLAYING")
                time.sleep(1)
                has_played = True

            if has_played:
                print("Finished: " + program)
            else:
                print("Failed: " + program)


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



if __name__ == "__main__":
    rt = RoboTelnet()
    rt.start()
