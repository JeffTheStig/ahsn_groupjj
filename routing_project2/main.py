import time

from aodv import *

if __name__ == "__main__":
    mnh = MainNodeHandler()

    while (1):
        for _, n in mnh.nodes.items():
            n.event_loop()
        
        time.sleep(0.010)