import re


class Plate:

    def __init__(self,id_,path):
        self.id = id_
        self.cur_step = 0
        self.path = path

        # Returns h_get['1'], should return h_get1
        self.path[0] = "h_get" + str(re.findall(r'[0-100]',self.path[0])) # Turn user input start position into protocol name
        self.add_paths()
        self.path.append("h_put") # Add hotel return as last command
        print(self.path)

    def add_paths(self):
        path = self.path

        for i in range(len(self.path)+1):
            add = 0
            print(i)
            if "washer" in self.path[i]:
                add += 1
                self.path.insert(i , "w_get")
            elif "dispenser" in self.path[i]:
                add += 1
                self.path.insert(i , "d_get")
            elif "shaker" in self.path[i]:
                add += 1
                self.path.insert(i , "s_get")
            i += add


    def step(self): # In case of more advanced step features in the future
        self.cur_step +=1
