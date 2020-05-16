import re

class BuildProtocol:

    HOTEL_SPOTS = 18
    SHAKER_SPOTS = 3
    LID_SPOTS = 3
    positions = []

    def __init__(self):

        def new_pos(st):
            self.positions.append(st)
            return st


        ## INPUT POSITION ##

        ## CHECKPOINT POSITIONS ###

        # hotel
        self.hg             = new_pos("h_get")
        self.hp             = new_pos("h_put")
        self.h_get          = [new_pos("h_get" + str(i + 1)) for i in range(self.HOTEL_SPOTS)]
        self.h_put          = [new_pos("h_put" + str(i + 1)) for i in range(self.HOTEL_SPOTS)]       
        self.h_checkPoint   = new_pos("h_checkPoint10")
        self.h_to_sw        = new_pos("h_to_sw")

        # washer
        self.w_get          = new_pos("sw_washerGet")
        self.w_put          = new_pos("sw_washerPut")
        self.washHigh_to_sw = new_pos("washHigh_to_sw")
        self.w_above        = new_pos("w_above")

        # dispenser
        self.d_get          = new_pos("d_get")
        self.d_put          = new_pos("d_put")
   
        # shaker
        self.s_get          = [new_pos("s_get" + str(i + 1)) for i in range(self.SHAKER_SPOTS)]
        self.s_put          = [new_pos("s_put" + str(i + 1)) for i in range(self.SHAKER_SPOTS)]

        # Switch
        self.sw_lidOff      = [new_pos("sw_lidOff" + str(i + 1)) for i in range(self.LID_SPOTS)]
        self.sw_lidOn       = [new_pos("sw_lidOn"  + str(i + 1)) for i in range(self.LID_SPOTS)]
        self.sw_safeHor     = new_pos("sw_safeHor")
        self.sw_getHor      = new_pos("sw_getHor")
        self.sw_putHor      = new_pos("sw_putHor")
        self.sw_putHorHigh  = new_pos("sw_putHorHigh")
        self.sw_safeVer     = new_pos("sw_safeVer")
        self.sw_getVer      = new_pos("sw_getVer")
        self.sw_putVer      = new_pos("sw_putVer")
        self.sw_to_h        = new_pos("sw_to_h")
        self.sw_to_washHigh = new_pos("sw_to_washHigh")   
        self.gripper_open   = new_pos("griperOpen")
        self.horToVer       = new_pos("sw_safe_horToVer")
        self.verToHor       = new_pos("sw_safe_verToHor")

        # Other devices
        self.washer_play    = new_pos("washer")
        self.dispenser_play = new_pos("dispenser")
        self.shaker_play    = new_pos("shaker")
        self.washer_wait    = new_pos("washer_wait")
        self.dispenser_wait = new_pos("dispenser_wait")
        self.shaker_wait    = new_pos("shaker_wait")

        self.device_list = [self.washer_play,self.dispenser_play,self.shaker_play]


    def build_protocol(self, movement,event_server,plate_id):

        es = event_server
        # Load protocol file
        # with open(file) as f:
        #     self.protocol = f.read().splitlines()
        
        # add_checkpoints = False if "_cp" in file else True
        # if add_checkpoints == True:
        self.protocol = movement # List contains current pos and destination pos
        for f in movement: # Added checkpoints to inputed list
            def cp(spot, value,a):
                self.protocol.insert(spot+1+a,value)
                return a + 1
                
            # Define spot here or in runner? Probably here
            def put_lid_on(): 
                #Add lid on protocol 
                spot = es.get_lid_spot(plate_id)
                a = cp(i,self.sw_lidOn[spot],a)
            def put_lid_off():
                spot = es.get_lid_spot(plate_id)
                a = cp(i,self.sw_putHor,a)
                a = cp(i,self.sw_lidOff[spot],a)

            def switch_to_ver(has_plate):
                if has_plate:
                    a = cp(i,self.sw_putHor,a)
                    a = cp(i,self.gripper_open,a)
                    a = cp(i,self.horToVer,a)
                    a = cp(i,self.sw_getVer,a)
                else:
                    a = cp(i,self.horToVer,a)
            
            def switch_to_hor(has_plate):
                if has_plate:
                    a = cp(i,self.sw_putVer,a)
                    a = cp(i,self.gripper_open,a)
                    a = cp(i,self.verToHor,a)
                    a = cp(i,self.sw_getHor,a)
                else:
                    a = cp(i,self.verToHor,a)

            def free_hotel_spot(): # Find free hotel spot
                return 0


            # Add checkpoints
            p = self.protocol
            a = 0 # handles offsets in the list
            for i in range(len(p)): # Added proper check points at each step
                s = str(p[i+a]) if len(p) > i+a else str(p[-1]) # current step
                sn = str(p[i+1+a]) if len(p) > i+a+1 else s # next step

                # ignore checking device-play steps
                # for d in self.device_list:
                #     if d in sn:
                #         a += 1
                #         sn = str(p[i+1+a]) if len(p) != i+a+1 else s

                # Update: new(from,to,cp_list[])
                # num1 = re.findall(r'\d+',s)
                # num2 = re.findall(r'\d+',sn)
                # if num1 and num2: # (Should have more checks then just numbers)
                #     dif = abs(int(num1[0])-int(num2[0]))
                #     if dif >= 10: # Hotel to hotel, too far away
                #         a = cp(i,self.h_checkPoint,a)


                # Add proper lid and delidding, side function
                # Determine shaker path

                if s in self.h_get:
                    if sn in self.washer_play:
                        a = cp(i,self.h_to_sw,a)
                        put_lid_off()
                        a = cp(i,self.sw_to_washHigh,a)
                        a = cp(i,self.w_put,a)
                    elif sn in self.dispenser_play:
                        a = cp(i,self.h_to_sw,a)
                        switch_to_ver(True)
                        a = cp(i,self.d_put,a)
                    elif sn in self.shaker_play:
                        # Add shaker CP
                        a = cp(i,self.s_put,a)
                elif s in self.washer_play:
                    if sn in self.d_get:
                        a = cp(i,self.washHigh_to_sw,a)
                        switch_to_ver(False)
                    elif sn in self.w_get:
                        break;
                    elif sn in self.s_get:
                        # Add shaker CP
                        break;
                    elif sn in self.h_get:
                        a = cp(i,self.washHigh_to_sw,a)
                        a = cp(i,self.sw_to_h,a)
                elif s in self.dispenser_play:
                    if sn in self.d_get:
                        break;
                    elif sn in self.w_get:
                        switch_to_ver(False)
                        a = cp(i,self.sw_to_washHigh,a)
                    elif sn in self.s_get:
                        # Add shaker CP
                        break;
                    elif sn in self.h_get:
                        switch_to_hor(False)
                        a = cp(i,self.sw_to_h,a)
                elif s in self.shaker_play:
                    if sn in self.d_get:
                        # Add shaker CP
                        break;
                    elif sn in self.w_get:
                        # Add shaker CP
                        break;
                    elif sn in self.s_get:
                        break;
                    elif sn in self.h_get:
                        # Add shaker CP
                        break;
                elif s in self.d_get:
                    if sn in self.washer_play:
                        switch_to_hor(True)
                        a = cp(i,self.sw_to_washHigh,a)
                        a = cp(i,self.w_put,a)
                    elif sn in self.dispenser_play:
                        a = cp(i,self.d_put,a)
                    elif sn in self.shaker_play:
                        # Add shaker CP
                        a = cp(i,self.s_put,a)
                    elif sn in self.h_put:
                        switch_to_hor(True)
                        put_lid_on()
                        a = cp(i,self.sw_to_h,a)
                        a = cp(i,self.h_put[free_hotel_spot()],a)                 
                elif s in self.w_get:
                    if sn in self.washer_play:
                        a = cp(i,self.w_put,a)
                    elif sn in self.dispenser_play:
                        a = cp(i,self.washHigh_to_sw,a)
                        switch_to_ver(True)
                        a = cp(i,self.d_put,a)
                    elif sn in self.h_put:
                        a = cp(i,self.washHigh_to_sw,a)
                        put_lid_on()
                        a = cp(i,self.sw_to_h,a)
                        a = cp(i,self.h_put[free_hotel_spot()],a)  
                    elif sn in self.shaker_play:
                        # Add shaker CP
                        a = cp(i,self.s_put,a)
                elif s in self.s_get:
                    if sn in self.washer_play:
                        # Add shaker CP
                        a = cp(i,self.w_put,a)
                    elif sn in self.dispenser_play:
                        # Add shaker CP
                        a = cp(i,self.d_put,a)
                    elif sn in self.h_put:
                        # Add shaker CP
                        a = cp(i,self.h_put[free_hotel_spot()],a) 
                    elif sn in self.shaker_play:
                        a = cp(i,self.s_put,a)


               

            # Build and return new file
            with open("file" + '_cp','w') as f:
                for x in self.protocol:
                    f.write(str(x) +'\n')

            return self.protocol

        
# if __name__ == "__main__":
#     b = BuildProtocol()
#     b.build_protocol()
#     print(b.protocol)
#     print(len(b.protocol))



# DUMP
