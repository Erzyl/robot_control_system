import re


class Plate:

    def __init__(self,id_,path):
        self.id = id_
        self.cur_step = 0
        self.path = path

        self.get_num = re.findall(r'[0-9]+',self.path[0])
        self.path[0] = "h_get" + self.get_num[0] # Turn user input start position into protocol name
        self.add_paths()
        self.path.append("h_put") # Add hotel return as last command
        print(self.path)


    def add_paths(self):

        for i in range(len(self.path)+1):
      
            if "washer" in self.path[i]:
                self.path.insert(i+1 , "w_get")
            elif "dispenser" in self.path[i]:

                self.path.insert(i+1 , "d_get")
            elif "shaker" in self.path[i]:
                
                self.path.insert(i+1 , "s_get")
            

    def step(self): # In case of more advanced step features in the future
        self.cur_step +=1
