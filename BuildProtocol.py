import re
import time

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
        self.w_get          = new_pos("w_get")
        self.w_put          = new_pos("w_put")
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


    def get_spot(self,plate_id,lista):
        try:
            return lista.index(plate_id)
        except ValueError:
            return -1



    def build_protocol(self, movement,plate_id, data_list):

        hotel_spots = data_list[0]
        lid_spots = data_list[1]

        
        self.protocol = movement # List contains current pos and destination pos

        a = 0 # handles offsets in the list

        def cp(spot, value,a):
            self.protocol.insert(spot+1+a,value)
            return a + 1

        def put_lid_on(a):
            #Add lid on protocol
            spot = self.get_spot(plate_id,lid_spots)
            a = cp(i,self.sw_lidOn[spot],a)
            return a

        def put_lid_off(a):
            spot = self.get_spot(plate_id,lid_spots)
            a = cp(i,self.sw_putHor,a)
            a = cp(i,self.sw_lidOff[spot],a)
            return a

        def switch_to_ver(has_plate,a):
            if has_plate:
                a = cp(i,self.sw_putHor,a)
                a = cp(i,self.gripper_open,a)
                a = cp(i,self.horToVer,a)
                a = cp(i,self.sw_getVer,a)
            else:
                a = cp(i,self.horToVer,a)
            return a

        def switch_to_hor(has_plate,a):
            if has_plate:
                a = cp(i,self.sw_putVer,a)
                a = cp(i,self.gripper_open,a)
                a = cp(i,self.verToHor,a)
                a = cp(i,self.sw_getHor,a)
            else:
                a = cp(i,self.verToHor,a)
            return a

        def put_in_hotel(a): # Find free hotel spot
            a += 1
            spot = self.get_spot(plate_id,hotel_spots)
            self.protocol[len(self.protocol)-1] = self.h_put[spot]
            return a


        # Add checkpoints
        p = self.protocol
        
        for i in range(len(p)): # Incase a longer main path should be built in one go in the future
            # a handles offsets in the list
            s = str(p[i+a]) if len(p) > i+a else str(p[-1]) # current step
            sn = str(p[i+1+a]) if len(p) > i+a+1 else s # next step

            print("Building path from: " +s)
            print("to: " +sn)

            a = cp(i,self.h_checkPoint,a)

            s_num = re.findall(r'[0-9]+',s)
            sn_num = re.findall(r'[0-9]+',sn)
    
            if (self.hg in sn or self.hp in sn): # Going to a hotel spot
                if s_num < HOTEL_SPOTS/2: # Need extra checkpoint if going to bottom half
                    a = cp(i,self.h_checkPoint)
            elif (self.hg in s or self.hp in s): # If last spot was hotel and next isn't
                if s_num < HOTEL_SPOTS/2:
                    a = cp(i,self.h_checkPoint)


            # Add proper lid and delidding, side function
            # Determine shaker path
            if s in self.hg and sn in self.hg: # Go from starting pos to
                break
            elif self.hg in s:
                if self.washer_play in sn:
                    a = cp(i,self.h_to_sw,a)
                    a = put_lid_off(a)
                    a = cp(i,self.sw_to_washHigh,a)
                    a = cp(i,self.w_put,a)
                elif self.dispenser_play in sn:
                    a = cp(i,self.h_to_sw,a)
                    a = switch_to_ver(True,a)
                    a = cp(i,self.d_put,a)
                elif self.shaker_play in sn:
                    # Add shaker CP
                    a = cp(i,self.s_put,a)
            elif self.washer_play in s:
                if sn in self.d_get:
                    a = cp(i,self.washHigh_to_sw,a)
                    a = switch_to_ver(False,a)
                elif sn in self.w_get:
                    break;
                elif sn in self.s_get:
                    # Add shaker CP
                    break;
                elif self.hg in sn:
                    a = cp(i,self.washHigh_to_sw,a)
                    a = cp(i,self.sw_to_h,a)
            elif self.dispenser_play in s:
                if sn in self.d_get:
                    break;
                elif sn in self.w_get:
                    a = switch_to_ver(False,a)
                    a = cp(i,self.sw_to_washHigh,a)
                elif sn in self.s_get:
                    # Add shaker CP
                    break;
                elif self.hg in sn:
                    a = switch_to_hor(False,a)
                    a = cp(i,self.sw_to_h,a)
            elif self.shaker_play in s:
                if sn in self.d_get:
                    # Add shaker CP
                    break;
                elif sn in self.w_get:
                    # Add shaker CP
                    break;
                elif sn in self.s_get:
                    break;
                elif self.hg in sn:
                    # Add shaker CP
                    break;
            elif s in self.d_get:
                if self.washer_play in sn:
                    a = switch_to_hor(True,a)
                    a = cp(i,self.sw_to_washHigh,a)
                    a = cp(i,self.w_put,a)
                elif self.dispenser_play in sn:
                    a = cp(i,self.d_put,a)
                elif self.shaker_play in sn:
                    # Add shaker CP
                    a = cp(i,self.s_put,a)
                elif self.hp in sn:
                    a = switch_to_hor(True,a)
                    a = put_lid_on(a)
                    a = cp(i,self.sw_to_h,a)
                    a = put_in_hotel(a)
            elif s in self.w_get:
                if self.washer_play in sn:
                    a = cp(i,self.w_put,a)
                elif self.dispenser_play in sn:
                    a = cp(i,self.washHigh_to_sw,a)
                    a = switch_to_ver(True,a) ####
                    a = cp(i,self.d_put,a)
                elif self.hp in sn: #######
                    a = cp(i,self.washHigh_to_sw,a)
                    a = put_lid_on(a)
                    a = cp(i,self.sw_to_h,a)
                    a = put_in_hotel(a)
                elif self.shaker_play in sn:
                    # Add shaker CP
                    a = cp(i,self.s_put,a)
            elif s in self.s_get:
                if self.washer_play in sn:
                    # Add shaker CP
                    a = cp(i,self.w_put,a)
                elif self.dispenser_play in sn:
                    # Add shaker CP
                    a = cp(i,self.d_put,a)
                elif sn in self.h_put:
                    # Add shaker CP
                    a = put_in_hotel(a)
                elif self.shaker_play in sn:
                    a = cp(i,self.s_put,a)


            self.protocol.pop(0) # Remove first item as its only a pointer for where to go from
            print("Protocol built!")
            # Build and return new file
            # with open("file" + '_cp','w') as f:
            #     for x in self.protocol:
            #         f.write(str(x) +'\n')

            return self.protocol


# if __name__ == "__main__":
#     b = BuildProtocol()
#     b.build_protocol()
#     print(b.protocol)
#     print(len(b.protocol))
