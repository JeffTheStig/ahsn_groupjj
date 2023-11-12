import sys, json, pickle
# from socket import *
import os.path
import random
import math
import time

from threading import Timer

TIMEOUT = 50

#------------------------------------------------------------------
# Functions
#------------------------------------------------------------------
class MainNodeHandler:
    def __init__(self, num_nodes, seed):
        self.nodes = dict()
        random.seed(seed)
        for i in range(num_nodes):
            node_id = chr(ord('A') + i)
            neighbours = []
            coords = (random.uniform(0, 100), random.uniform(0, 100))
            routing_table = []
            self.nodes[node_id] = AodvNode(self, node_id, neighbours, coords, routing_table)
        
        self.RREQ_count = 0
        self.packet_created = 0
        self.packet_send = 0
        self.packet_arrived = 0
        self.packet_send_after_RREP = 0
        self.reply_send = 0
        self.reply_arrived = 0

        self.RREQ_forwards = 0
        self.RREQ_send = 0
        self.RREP_send = 0
        self.RERR_send = 0
        self.packet_forwards = 0
        self.timer_timeouts = 0
        self.broken_paths = 0
        self.RREP_after_in_rt = 0
        self.TTL_timouts = 0
        self.neighbour_oo_range = 0

        self.dsr = False
        self.dsr_TTL = 10

        self.packet_delay_s = 0
        self.packet_delay_steps = 0

        self.packets_created_main = 0

    def sendMessage(self, id: str, message: str, sender: str, timer_id: int):
        if id in self.nodes and sender in self.nodes:
            if id in self.nodes[sender].neighbours:
                self.nodes[id].receiveMessage(sender, message, timer_id)
            else:
                print(f"[ERROR] Receiving node {id} not in range of sender {sender} anymore!")
                self.nodes[sender].neighbour_timeout(id)
                self.neighbour_oo_range += 1

    def getNodes(self):
        return self.nodes

    def find_neighbours(self, max_range):
        node_items = list(self.nodes.items())
        for i in range(len(node_items)):
            node_x_id, node_x = node_items[i]
            for j in range(i + 1, len(node_items)):
                node_y_id, node_y = node_items[j]
                if node_x_id == node_y_id:
                    continue

                x_diff = node_x.coords[0] - node_y.coords[0]
                y_diff = node_x.coords[1] - node_y.coords[1]
                curr_dist = math.sqrt((x_diff * x_diff) + (y_diff * y_diff))

                if curr_dist <= max_range:
                    if node_y_id not in node_x.neighbours:
                        node_x.neighbours.append(node_y.nodeId)
                        node_y.neighbours.append(node_x.nodeId)
                else:
                    if node_y_id in node_x.neighbours:
                        node_x.neighbours.remove(node_y_id)
                        node_y.neighbours.remove(node_x_id)

        # print("Finished finding neighbours!")
        # for node_x_id, node_x in self.nodes.items():
        #     print(node_x_id, " neighbhours:", node_x.neighbours)

    def move_nodes(self, max_dist, maxw, maxh):
        for _, node in self.nodes.items():
            node.prev_coords = node.coords
            node.coords = (min(max(random.uniform(node.coords[0] - max_dist / 2, node.coords[0] + max_dist / 2), 0), maxw),
                       min(max(random.uniform(node.coords[1] - max_dist / 2, node.coords[1] + max_dist / 2), 0), maxh));

        # for _, node in self.nodes.items():
        #     node.prev_coords = node.coords
        #     x_offset = random.uniform(-max_dist/4, max_dist/4)
        #     y_offset = random.uniform(-max_dist/4, max_dist/4)
        #     if node.prev_coords is not None:
        #         prev_x, prev_y = node.prev_coords
        #         curr_x, curr_y = node.coords
        #         x_diff = curr_x - prev_x
        #         y_diff = curr_y - prev_y
        #         x_offset += random.uniform(-max_dist/8, max_dist/8) + x_diff/1.5
        #         y_offset += random.uniform(-max_dist/8, max_dist/8) + y_diff/1.5
        #     node.coords = (min(max(node.prev_coords[0] + x_offset, 0), maxw), min(max(node.prev_coords[1] + y_offset, 0), maxh))


        # print(self.nodeId, "moved from", self.prev_coords, "to", self.coords)

class AodvNode:
    def __init__(self, mnh: MainNodeHandler, nodeId: str, neighbours: list, coords: tuple, routing_table: list):
        self.nodeId = nodeId
        self.seq_no = 1
        self.broadcast_no = 1
        self.nodePort = 0
        self.life_time = "inf"
        self.routingTable = []
        self.neighbours = neighbours
        self.routeEntry = []
        self.hop_count = 0
        self.dest_id = ""
        self.dest_seq = -1	
        self.RREQ = []
        self.RREP_B = []
        self.RREP_F = []
        self.RREP = []
        self.RERR = []
        self.TIMEOUT = 10
        # self.timers = dict()
        self.mnh = mnh
        self.input_buff = []
        self.coords = coords
        self.prev_coords = coords
        self.neighbour_timeout_arg = None
        self.timer_count = 0
        self.rreqs = dict()
        self.message = []
        self.replying = False
        self.replying_prev_timer = -1

        # print("---------------------------")
        # print("node:", self.nodeId, " coordinates:", self.coords)
        # print("---------------------------")

        # print("-----------------------------------------")
        # print("Neighbours: ", self.neighbours)
        # print("-----------------------------------------")

        #sending mode
        if (nodeId == "A"):
            self.flag = "0"
        else:
            self.flag = "2"

    def receiveMessage(self, id: str, msg: str, timer_id: int):
        self.input_buff.append([msg, id, timer_id])

    def checkRoutingTable(self, dest):
        all_dest = [x[0] for x in self.routingTable]
        if (dest in all_dest):
            return True
        return False

    def showRoutingTable(self):
        # print("-----------------------------------------------------------------------------------")
        # print("|                                Routing Table                                    |")
        # print("-----------------------------------------------------------------------------------")
        # print("|  Destination  | Next Hop | Hop Count | Life Time | Destination Sequence | Valid |")
        # print("-----------------------------------------------------------------------------------")
        # for x in range(0,len(self.routingTable)):
        #     dest = self.routingTable[x][0]
        #     n_h = self.routingTable[x][1]
        #     h_c = self.routingTable[x][2]
        #     l_t = self.routingTable[x][3]
        #     dest_sequence = self.routingTable[x][4]
        #     valid = self.routingTable[x][5]

        #     row = "|  "+dest+"| ".rjust(15-len(dest))+n_h+"|   ".rjust(13-len(n_h))+str(h_c)+"| ".rjust(10-len(str(h_c)))+l_t+" | ".rjust(10-len(l_t))+"   "+str(dest_sequence)+"| ".rjust(20-len(str(dest_sequence)))+" "+str(valid)+"    |"
        #     print(row)
        # print("-----------------------------------------------------------------------------------")
        hello = "world"

    def showRoutingTable2(self):
        print("-----------------------------------------------------------------------------------")
        print("|                                Routing Table                                    |")
        print("-----------------------------------------------------------------------------------")
        print("|  Destination  | Next Hop | Hop Count | Life Time | Destination Sequence | Valid |")
        print("-----------------------------------------------------------------------------------")
        for x in range(0,len(self.routingTable)):
            dest = self.routingTable[x][0]
            n_h = self.routingTable[x][1]
            h_c = self.routingTable[x][2]
            l_t = self.routingTable[x][3]
            dest_sequence = self.routingTable[x][4]
            valid = self.routingTable[x][5]

            row = "|  "+dest+"| ".rjust(15-len(dest))+n_h+"|   ".rjust(13-len(n_h))+str(h_c)+"| ".rjust(10-len(str(h_c)))+l_t+" | ".rjust(10-len(l_t))+"   "+str(dest_sequence)+"| ".rjust(20-len(str(dest_sequence)))+" "+str(valid)+"    |"
            print(row)
        print("-----------------------------------------------------------------------------------")

    # def getNodeName(self, port):
    #     for x in self.neighbours.items():
    #         if (x[1][2] == port):
    #             return x[1]

    def getNextHop(self, dest):
        for x in self.routingTable:
            if (x[0] == dest):
                return x[1]

    def getEntry(self, dest_id):
        for x in self.routingTable:
            if (x[0] == dest_id):
                return x

    def sendRERR(self, destId, destSeq):
        source = self.nodeId
        dest_count = 1
        destSeq = destSeq+1
        RERR = ["RERR", source, dest_count, destId, destSeq]
        #broadcasting RERR to neighbours
        for x in self.neighbours:
            RERR = json.dumps(RERR)
            # self.sock.sendto(RERR, (neighbour_node[1], neighbour_node[2]))	
            self.mnh.sendMessage(x, RERR, self.nodeId, -1)
            print(f"[RERR] {self.nodeId}->{x}")
        self.mnh.RERR_send += 1

    def neighbour_timeout(self, neigh_id):
        i = 0

        self.mnh.timer_timeouts += 1
        for x in self.routingTable:
            next_hop_id = x[1]
            if (neigh_id == next_hop_id):
                self.routingTable[i][5] = 0
            i+=1
        entry = self.getEntry(neigh_id)
        #destination and dest seq no
        if entry != None:
            self.sendRERR(neigh_id, entry[4])
        # else:
        #     self.sendRERR(neigh_id, -1)
        print("Timeout triggered for", neigh_id)
        self.showRoutingTable()

    def event_loop(self, step):
        # for i in self.timers:
        #     self.timers[i][0] = self.timers[i][0] - 1

        #     if self.timers[i][0] == 0:
        #         self.timers[i][1](self.timers[i][2]) # If timer ran out, trigger function

        # self.timer = self.timer - 1

        # if (self.timer == 0 and self.neighbour_timeout_arg != None):
        #     self.neighbour_timeout(self.neighbour_timeout_arg)
        #sending mode
        if (self.flag == "0"):
            self.dest_id = random.choice([id for id, _ in self.mnh.nodes.items() if id != self.nodeId])
            print(f"[AODV] Node {self.nodeId} wants to send to {self.dest_id}")
            self.flag = "1"
            self.mnh.packet_created += 1

            sender = self.nodeId
            receiver = self.dest_id
            message = f"[{self.nodeId}] Hello world!"
            data = json.dumps(["DATA",sender,receiver,message])
            self.message = data
            
        if (self.flag == "1"):
            # dest_id = "dawood"
            #input("Name of destination node: ")
            #if it has destination route in its own table
            if (self.checkRoutingTable(self.dest_id)):
                print("[LOG] I have active route to destination")
                print("[DATA] Sending message...")
                # sender = self.nodeId
                # receiver = self.dest_id
                # message = f"[{self.nodeId}] Hello world!"
                # data = json.dumps(["DATA",sender,receiver,message])

                if self.replying:
                    self.mnh.sendMessage(self.getNextHop(self.dest_id), self.message, self.nodeId, self.replying_prev_timer)
                    self.replying = False
                    self.mnh.reply_send += 1
                else:
                    # self.timer_count += 1
                    self.mnh.packet_send += 1
                    # self.timers[self.timer_count] = (Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(self.dest_id)]), -1) # Storing timer and timerId of previous node
                    # self.timers[self.timer_count][0].start()
                    # self.timers[self.timer_count] = [TIMEOUT, self.neighbour_timeout, self.getNextHop(self.dest_id), -1] # Storing timer and timerId of previous node
                    # self.sock.sendto(data, tuple(self.getNextHop(self.dest_id)))

                    # self.timer = self.TIMEOUT
                    # self.neighbour_timeout_arg = self.getNextHop(self.dest_id)
                    self.mnh.sendMessage(self.getNextHop(self.dest_id), self.message, self.nodeId, self.timer_count)
                    # self.mnh.packet_send_immediately += 1
                self.showRoutingTable2()
                self.flag = "2"
            else:
                print(f"[LOG] I don't have route to destination {self.dest_id}")
                print("[LOG] Let me discover the route.")
                #broadcasting RREQ to neighbours
                for x in self.neighbours:
                    # neighbour_node = self.neighbours.get(ns[x])
                    RREQ = ["RREQ", self.nodeId, self.seq_no, self.broadcast_no, self.dest_id, self.dest_seq, 0, self.mnh.dsr_TTL]
                    RREQ = json.dumps(RREQ)
                    # self.sock.sendto(RREQ, (neighbour_node[1], neighbour_node[2]))
                    self.mnh.sendMessage(x, RREQ, self.nodeId, -1)	
                    print("[RREQ]", self.nodeId, "->", x)
                self.mnh.RREQ_send += 1
                self.rreqs[self.dest_id] = [step, time.time()]
                self.flag = "2"
                
                self.mnh.RREQ_count += 1
                    
        #receiving mode
        elif (self.flag == "2"):
            while self.input_buff:
                msg,clientId,timerPrev = self.input_buff.pop(0)
                msg = json.loads(msg)
                #if it is RREQ packet
                self.showRoutingTable()
                if (msg[0] == "RREQ"):
                    #["RREQ", src_id, src_seq, src_brdcst, dest_id, dest_seq, hops]
                    print("[RREQ]",self.nodeId, "<-", clientId)
                    if self.mnh.dsr:
                        msg[7] = msg[7] - 1 # Decrease TTL
                    if msg[7] <= 0:
                            print(f"[TTL] Timout on node {self.nodeId}, destination was {msg[4]}")
                            self.mnh.TTL_timouts += 1
                    else:
                        # if originator of RREQ is already in routing table or originator is receiving RREQ back to itself
                        curr_entry = self.getEntry(msg[1])

                        if (curr_entry is not None and curr_entry[4] > msg[6]+1): # If current hopcount is bigger then request hopcount, delete reverse entry.
                            self.routingTable.remove(curr_entry)
                        
                        if (curr_entry is not None): # If there is already an entry:
                            print(f"[DUP] {self.nodeId} Discarded RREQ from",  msg[1])
                        elif (msg[1] == self.nodeId):
                            # if (self.getEntry(clientId) is not None): # If we are the sender and there is already a route present
                            #     self.routingTable.remove(self.getEntry(clientId))
                            self.routingTable.append([clientId, clientId, 1, self.life_time, msg[5], 1])
                            print(f"Table update for {self.nodeId}: {self.routingTable[-1]}")
                        else:
                            if (msg[1] != self.nodeId):
                                #add reverse entry in routing table
                                self.routingTable.append([msg[1], clientId, msg[6]+1, self.life_time, msg[5], 1])
                                print(f"Table update for {self.nodeId}: {self.routingTable[-1]}")
                                #serialize the routing table
                            
                            #if node has destination route in routing table
                            if (self.checkRoutingTable(msg[4]) and not self.mnh.dsr):
                                print("[LOG] I have active route to destination")
                                self.mnh.RREP_after_in_rt += 1
                                routeEntry = self.getEntry(msg[4])
                                dest_seq = self.seq_no	#RFC3561: 6.6.2	
                                RREP_B = ["RREP", routeEntry[0], dest_seq, msg[1], routeEntry[2], routeEntry[3]]
                                RREP_B = json.dumps(RREP_B)

                                RREP_F = ["RREP", routeEntry[0], dest_seq, msg[1], msg[6], routeEntry[3]]
                                RREP_F = json.dumps(RREP_F)
                                
                                # self.sock.sendto(RREP, tuple(self.getNextHop(msg[1][0])[1:]))
                                self.mnh.sendMessage(self.getNextHop(msg[1]), RREP_B, self.nodeId, timerPrev)
                                self.mnh.sendMessage(self.getNextHop(msg[4]), RREP_F, self.nodeId, -1)
                                print("[RREP]", self.nodeId, "->", msg[1])
                                self.mnh.RREP_send += 1
                            #if routing entry is to be updated
                            else:
                                #if originator of RREQ is not receiving RREQ back from it's neighbours
                                destination = msg[4]		#destination_id
                                #If RREQ is reached at destination
                                if (self.nodeId == destination):
                                    print("[LOG] I'm the destination")
                                    dest_seq = msg[2]+1
                                    hop_count = 0
                                    RREP = ["RREP", self.nodeId, dest_seq, msg[1], hop_count, "infinite"]
                                    #serialize the RREP list into json
                                    RREP = json.dumps(RREP)
                                    #send data to Next_hop that leads to destination
                                    # self.sock.sendto(RREP, tuple(self.getNextHop(msg[1][0])[1:]))
                                    self.mnh.sendMessage(self.getNextHop(msg[1]), RREP, self.nodeId, timerPrev)
                                    print("[RREP]", self.nodeId, "->", self.getNextHop(msg[1]))
                                    self.mnh.RREP_send += 1
                                else:
                                    print(f"[LOG] I don't have route to destination {destination} from RREQ")
                                    print("[LOG] Let me discover the route.")
                                    self.mnh.RREQ_forwards += 1
                                    #get node_ids of all neighbours
                                    # ns = list(self.neighbours.keys())
                                    #increment hop count
                                    msg[6] = msg[6]+1
                                    #broadcasting RREQ to neighbours
                                    for x in self.neighbours:
                                        #get neighbour node => [node_id, node_ip, node_port]
                                        # neighbour_node = self.neighbours.get(ns[x])
                                        #serialize the RREQ list into json
                                        RREQ = json.dumps(msg)
                                        #send data to neighbours
                                        # self.sock.sendto(RREQ, (neighbour_node[1], neighbour_node[2]))	
                                        self.mnh.sendMessage(x, RREQ, self.nodeId, -1)
                                        print("[RREQ]", self.nodeId,"->", x)
                                    self.mnh.RREQ_send += 1

                #if it is RREP packet
                elif(msg[0] == "RREP"):
                    #print msg
                    print("[RREP]",self.nodeId, "<-", clientId)
                    if (self.checkRoutingTable(msg[1])):
                        h_count = self.getEntry(msg[1])[2]
                        if (h_count > msg[4]+1):
                            self.routingTable.remove(self.getEntry(msg[1]))
                            self.routingTable.append([msg[1], clientId, msg[4]+1, self.life_time, msg[2],1])
                            print(f"Table update for {self.nodeId}: {self.routingTable[-1]}")
                    else:
                        self.routingTable.append([msg[1], clientId, msg[4]+1, self.life_time, msg[2],1])
                        print(f"Table update for {self.nodeId}: {self.routingTable[-1]}")
                    
                    #if RREP is reached at originator of RREQ: means route found.
                    if (self.nodeId == msg[3]):
                        print("[SUCCESS] Route found")
                        print("[DATA] Sending message...next round")

                        if msg[1] in self.rreqs:
                            self.mnh.packet_delay_steps += step - self.rreqs[msg[1]][0]
                            self.mnh.packet_delay_s += time.time() - self.rreqs[msg[1]][1]
                            self.rreqs.pop(msg[1])
                            self.mnh.packet_send_after_RREP += 1
                        # sender = self.nodeId
                        # receiver = self.dest_id
                        # message = f"[{self.nodeId}] Hello World!"
                        # #serialize data list into json
                        # data = json.dumps(["DATA",sender,receiver,message])
                        # # timer = Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(dest_id)[0]])
                        # # timer.start()

                        # self.timer_count += 1
                        # # self.timers[self.timer_count] = (Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(self.dest_id)]), -1)
                        # # self.timers[self.timer_count][0].start()
                        # self.timers[self.timer_count] = [self.TIMEOUT, self.neighbour_timeout, self.getNextHop(self.dest_id), -1] # Storing timer and timerId of previous node

                        # # self.timer = self.TIMEOUT
                        # # self.neighbour_timeout_arg = self.getNextHop(self.dest_id)

                        # # self.sock.sendto(data, tuple(self.getNextHop(dest_id)[1:]))
                        # self.mnh.sendMessage(self.getNextHop(self.dest_id), data, self.nodeId, self.timer_count)
                        # self.showRoutingTable()
                        self.flag = "1"
                    else:
                        #hop count incrementing
                        msg[4] = msg[4]+1		
                        #serializing msg into json
                        RREP = json.dumps(msg)
                        #send data to Next_hop that leads to destination
                        # self.sock.sendto(RREP, tuple(self.getNextHop(msg[3][0])[1:]))
                        self.mnh.sendMessage(self.getNextHop(msg[3]), RREP, self.nodeId, -1)
                        print("[RREP]",self.nodeId,"->",self.getNextHop(msg[3]))
                    
                #if it is DATA packet
                elif (msg[0] == "DATA"):
                    #if data packet is received at destination
                    if (msg[2] == self.nodeId):
                        #print msg
                        print(msg[3])
                        source = self.nodeId
                        destination = msg[1]
                        message = f"[{self.nodeId}] Hello Back!"
                        #create reply msg and serialize into json
                        data = json.dumps(["REPLYDATA",source,destination,message])
                        #send data to Next_hop that leads to originator of data msg
                        # self.sock.sendto(data, tuple(self.getNextHop(destination)[1:]))

                        self.message = data
                        self.replying = True
                        self.replying_prev_timer = timerPrev
                        self.dest_id = msg[1]

                        # self.mnh.sendMessage(self.getNextHop(destination), data, self.nodeId, timerPrev)
                        self.flag = "1"

                        print(f"===========================Sending reply from {source} to {destination} next round")
                        # self.mnh.reply_send += 1
                        self.mnh.packet_arrived += 1
                        self.showRoutingTable2()
                    #if data packet is received at intermediate node (not at destination)
                    else:
                        if (self.checkRoutingTable(msg[2])):
                            # timer.cancel()
                            # timer = Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(msg[2])[0]])
                            # timer.start()

                            # self.timer_count += 1
                            # # self.timers[self.timer_count] = (Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(msg[2])]), timerPrev)
                            # # self.timers[self.timer_count][0].start()
                            # self.timers[self.timer_count] = [TIMEOUT, self.neighbour_timeout, self.getNextHop(msg[2]), timerPrev] # Storing timer and timerId of previous node
                            # print(f"Node {self.nodeId} created timer: {self.timer_count}")
                            # self.timer = self.TIMEOUT 
                            # self.neighbour_timeout_arg = self.getNextHop(msg[2])

                            # print that forwarding message to next hop
                            print(f"[LOG] forwarding message to {self.getNextHop(msg[2])}")
                            data = json.dumps(msg)
                            # self.sock.sendto(data, tuple(self.getNextHop(msg[2])[0]))
                            self.mnh.sendMessage(self.getNextHop(msg[2]), data, self.nodeId, self.timer_count)
                            self.mnh.packet_forwards += 1
                        else:
                            self.mnh.broken_paths += 1
                            self.sendRERR(msg[2], -1)
                            
                #if it is REPLYDATA packet
                elif (msg[0] == "REPLYDATA"):
                    #if packet is received at destination
                    destination_id = msg[2]
                    if (destination_id == self.nodeId):
                        # timer.cancel()

                        # # self.timers[timerPrev][0].cancel()
                        # print(f"Node {self.nodeId} Canceling {timerPrev}")
                        # self.timers.pop(timerPrev)

                        # self.timer = -1
                        print(msg[3])
                        self.mnh.reply_arrived += 1
                        print(f"===================================================Reply from {msg[1]} to {self.nodeId} arrived!")
                        # self.showRoutingTable2()
                    #if packet is at intermediate node, forward it to next hop
                    else:
                        # timer.cancel()
                        # timer = Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(destination_id)[0]])
                        # timer.start()

                        # self.timers[timerPrev][0].cancel()
                        # Save to not use timer here. Node will not know that the link broke during transmission but the node we are sending to right now will
                        # not trigger its send timer. 
                        # print(f"Node {self.nodeId} canceling timer {timerPrev}")
                        # tn = self.timers.pop(timerPrev)[3]

                        # self.timer = self.TIMEOUT
                        # self.neighbour_timeout_arg = self.getNextHop(destination_id)
                        

                        print("[LOG] forwarding message to", self.getNextHop(destination_id))
                        data = json.dumps(msg)
                        # self.sock.sendto(data, tuple(self.getNextHop(destination_id)[1:]))
                        # self.mnh.sendMessage(self.getNextHop(destination_id), data, self.nodeId, tn)
                        self.mnh.sendMessage(self.getNextHop(destination_id), data, self.nodeId, -1)

                #if it is RERR packet
                elif (msg[0] == "RERR"):
                    destination_id = msg[3]
                    i = 0
                    for x in self.routingTable:
                        next_hop_id = x[1]
                        if (destination_id == next_hop_id):
                            self.routingTable[i][5] = 0
                        i+=1
                    #if routingTable doesn't have any entry that has infected next hop
                    if (i == 0):
                        pass
                    else:
                        entry = self.getEntry(destination_id)
                        if entry != None:
                            self.sendRERR(destination_id, entry[4])
            self.showRoutingTable()

        else:
            print("Invalid Input.")


