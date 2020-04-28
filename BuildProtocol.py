import re


class BuildProtocol:

    HOTEL_SPOTS = 18
    positions = []

    def __init__(self):

        def new_pos(st):
            self.positions.append(st)
            return st

        ## MAIN POSITIONS ###

        # hotel
        self.hg             = new_pos("h_get")
        self.hp             = new_pos("h_put")
        self.h_get          = [new_pos("h" + str(i + 1) + "_get") for i in range(self.HOTEL_SPOTS)]
        self.h_put          = [new_pos("h" + str(i + 1) + "_put") for i in range(self.HOTEL_SPOTS)]

        # washer
        self.w_get          = new_pos("sw_washerGet")
        self.w_put          = new_pos("sw_washerPut")

        # dispenser
        self.d_get          = new_pos("d_get")
        self.d_put          = new_pos("d_put")
   
        # shaker
        self.s_get          = new_pos("s_get")
        self.s_put          = new_pos("s_put")

        ### CHECKPOINTS ###
        self.sw_safeHor     = new_pos("sw_safeHor")
        self.sw_getHor      = new_pos("sw_getHor")
        self.sw_putHor      = new_pos("sw_putHor")
        self.sw_putHorHigh  = new_pos("sw_putHorHigh")
        self.sw_safeVer     = new_pos("sw_safeVer")
        self.sw_getVer      = new_pos("sw_getVer")
        self.sw_putVer      = new_pos("sw_putVer")
        self.sw_lidOff      = new_pos("sw_lidOff")
        self.sw_lidOn       = new_pos("sw_lidOn")
        self.h_checkPoint   = new_pos("h_checkPoint10")
        self.h_to_sw        = new_pos("h_to_sw")
        self.sw_to_h        = new_pos("sw_to_h")
        self.sw_to_washHigh = new_pos("sw_to_washHigh")
        self.washHigh_to_sw = new_pos("washHigh_to_sw")
        self.w_above        = new_pos("w_above")
        self.gripper_open   = new_pos("griperOpen")
        self.horToVer       = new_pos("sw_safe_horToVer")
        self.verToHor       = new_pos("sw_safe_verToHor")

        ## Devices ##
        self.washer_play    = new_pos("washer")
        self.dispenser_play = new_pos("dispenser")
        self.shaker_play    = new_pos("shaker")
        self.washer_wait    = new_pos("washer_wait")
        self.dispenser_wait = new_pos("dispenser_wait")
        self.shaker_wait    = new_pos("shaker_wait")

        self.device_list = [self.washer_play,self.dispenser_play,self.shaker_play]


    def build_protocol(self, file = "protocol"):

        # Load protocol file
        with open(file) as f:
            self.protocol = f.read().splitlines()
        
        add_checkpoints = False if "_cp" in file else True
        if add_checkpoints == True:

            def cp(spot, value,a):
                self.protocol.insert(spot+1+a,value)
                return a + 1
                
            # Fix strings (Avoid by renaming all protocols with proper names)
            def fix_hotel_string(lis):  
                if "h" in lis:        
                    if any(map(str.isdigit,lis)):
                        if "_get" in lis:
                            return "h_get"
                        elif "_put" in lis:
                            return "h_put"
                return str(p[i])
        

            # Add checkpoints
            p = self.protocol
            a = 0 # handles offsets in the list
            for i in range(len(p)):
                s = str(p[i+a]) if len(p) > i+a else str(p[-1]) # current step
                sn = str(p[i+1+a]) if len(p) > i+a+1 else s # next step

                # ignore checking device-play steps
                for d in self.device_list:
                    if d in sn:
                        a += 1
                        sn = str(p[i+1+a]) if len(p) != i+a+1 else s

                # Update: new(from,to,cp_list[])
                num1 = re.findall(r'\d+',s)
                num2 = re.findall(r'\d+',sn)
                if num1 and num2: # (Should have more checks then just numbers)
                    dif = abs(int(num1[0])-int(num2[0]))
                    if dif >= 10: # Hotel to hotel, too far away
                        a = cp(i,self.h_checkPoint,a)
                elif s in self.w_put: # from washer put
                    if fix_hotel_string(sn) in self.hg: # to hotel get
                        a = cp(i,self.washHigh_to_sw,a)
                        a = cp(i,self.sw_to_h,a)
                    elif sn in self.d_get: # to dispenser get
                        a = cp(i,self.washHigh_to_sw,a)
                        a = cp(i,self.horToVer,a)
                elif s in self.d_put: # from dispenser put
                    if fix_hotel_string(sn) in self.hg: # to hotel get
                        a = cp(i,self.verToHor,a)
                        a = cp(i,self.sw_to_h,a)
                    elif sn in self.w_get: # to washer get
                        a = cp(i,self.verToHor,a)
                        a = cp(i,self.sw_to_washHigh,a)
                elif s in self.s_put:
                    print('Update shaker protocols!') 
                elif s in self.w_get:
                    if fix_hotel_string(sn) in self.hp:
                        a = cp(i,self.washHigh_to_sw,a)
                        a = cp(i,self.sw_putHorHigh,a)
                        a = cp(i,self.sw_getHor,a)
                        a = cp(i,self.sw_to_h,a)
                elif s in self.d_get:
                    if fix_hotel_string(sn) in self.hp:
                        a = cp(i,self.verToHor,a)
                        a = cp(i,self.sw_getHor,a)
                        a = cp(i,self.sw_to_h,a)
                elif s in self.s_get:
                    print('Update shaker protocols!')                      
                elif fix_hotel_string(s) in self.hg: # from hotel get
                    if sn in self.w_put: # to washer put
                        a = cp(i,self.h_to_sw,a)
                        a = cp(i,self.sw_putHor,a)
                        a = cp(i,self.sw_lidOff,a)
                        a = cp(i,self.sw_to_washHigh,a)
                    elif sn in self.d_put: # to disp put
                        a = cp(i,self.h_to_sw,a)
                        a = cp(i,self.sw_putHor,a)
                        a = cp(i,self.gripper_open,a)
                        a = cp(i,self.horToVer,a)
                elif fix_hotel_string(s) in self.hp: # from hotel put
                    if sn in self.w_get: # to washer get
                        a = cp(i,self.h_to_sw,a)
                        a = cp(i,self.sw_to_washHigh,a)
                    elif sn in self.d_get: # to dispenser get
                        a = cp(i,self.h_to_sw,a)
                        a = cp(i,self.horToVer,a)
                elif i + a <= len(p): # Should ignore decvice checks and expanded
                    print("This dosen't seem right. (If intended, add manualy to final protocol).")
                    print("Trying to go from {0} to {1}".format(s,sn))

            # Build and return new file
            with open(file + '_cp','w') as f:
                for x in self.protocol:
                    f.write(str(x) +'\n')

        
if __name__ == "__main__":
    b = BuildProtocol()
    b.build_protocol()
    print(b.protocol)
    print(len(b.protocol))



# DUMP
