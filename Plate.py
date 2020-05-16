import re


class Plate:

    def __init__(self,id_,path):
        self.id = id_
        self.cur_step = 0
        self.path = path
        self.path[0] = "h_get" + re.findall(r'\d+',self.path[0]) # Turn user input start position into protocol name
        self.add_paths()
        self.path.append("h_put")

    def add_paths(self):
        i = 0
        for p in self.path:
            if "washer" in p:
                list.insert(i , "w_get")
            elif "dispenser" in p:
                list.insert(i , "d_get")
            elif "shaker" in p:
                list.insert(i , "s_get")
            i += 1

    def step(self): # In case of more advanced step features in the future
        self.cur_step +=1 
