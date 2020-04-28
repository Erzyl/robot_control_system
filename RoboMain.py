from BuildProtocol import BuildProtocol
from RoboRun import RoboRun
from RoboConnect import RoboConnect

class RoboMain:

    p = BuildProtocol()
    c = RoboConnect()
    r = RoboRun()

    p.build_protocol("protocol") # Pass in a file with "_cp" to avoid building checkpoints
    c.connect()
    
    r.start(c.tn, p.protocol)

