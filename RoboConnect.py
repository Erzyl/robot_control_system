import telnetlib
#import traceback

class RoboConnect:
    HOST = "130.238.44.58"
    PORT = 29999

    def __init__(self):
        self.tn = -1

    def connect(self):
        #try:
        print("Connecting..")
        self.tn = telnetlib.Telnet(self.HOST, self.PORT)
        self.tn.read_until(b"Dashboard Server")
        # except Exception as e:
        #     print("No connection could be established..")
        #     #traceback.print_exc()

        # self.tn.write('AT'+"\r")
        # if self.tn.read_until("OK"):
        #     print("Connection established!")


if __name__ == "__main__":
    r = RoboConnect()
    r.connect()