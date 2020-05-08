

class Plate:

    def __init__(self,id_,path):
        self.id = id_
        self.cur_step = 0
        self.current = path[self.cur_step]
        self.destination = path[self.cur_step+1]
        self.path = path
        

    def step(self):
        self.cur_step +=1 
        self.current = self.path[self.cur_step]
        self.destination = self.path[self.cur_step+1]