# Echo client program
import socket
import time
import telenetlib




# SOCKET CONNECTION
HOST_sock = "192.168.0.9"
PORT_sock = 30002
connected_sock = 0

# TELNET CONNECTION
HOST_tel = "130.238.44.58"
PORT_tel = 29999
connect_tn = 0

# Cords
cord = "[-0.5405182705025187, -2.350330184112267, -1.316631037266588, -2.2775736604458237, 3.3528323423665642, -1.2291967454894914]"
prog = b"/programs/h13.urp"
go_start = 1


# Connect Socket

print("Setting up socket connection")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST_sock, PORT_sock))
time.sleep(2)
self.connected_sock = 1


# Connect telnet
tn = telenetlib.Telnet(HOST_tel, PORT_tel)
tn.read_until(b"Dashboard Server")


# Run
while connected_sock == 1:

    if go_start == 1:
        self.tel_cmd(b"load " + prog)
        self.move_to(cord)
        go_start = 2
    elif go_start == 2:
        self.tel_cmd(b"play")
        time.sleep(2)
        is_running = tn.read_eager().decode('ascii')
        if is_running == "Starting program":
            go_start = 0


# Methods
def move_to(cords):
    s.send ("movej(" + cords + ", a=1.3962634015954636, v=1.0471975511965976)" + "\n")


def tel_cmd():
    tn.write(cmd + b"\n")


def shutdown():
    data = s.recv(1024)
    print ("Received", repr(data))
    s.close()
    tn.close()
    print("Program finish")
