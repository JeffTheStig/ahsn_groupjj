import sys, json, pickle
# from socket import *
import os.path
import random
import math

#------------------------------------------------------------------
# Functions
#------------------------------------------------------------------
class MainNodeHandler:
    def __init__(self, num_nodes):
        self.nodes = dict()
        #self.nodes["A"] = AodvNode(self, "A", ["B"], (0,0), ["B", "B", 0, "inf", ["B"], True])
        #self.nodes["B"] = AodvNode(self, "B", ["A"], (0,0), ["A", "A", 0, "inf", ["A"], True])
        for i in range(num_nodes):
            node_id = chr(ord('A') + i)
            neighbours = []
            coords = (random.uniform(0, 100), random.uniform(0, 100))
            routing_table = []
            self.nodes[node_id] = AodvNode(self, node_id, neighbours, coords, routing_table)
        
        self.RREQ_count = 0
        self.packet_created = 0
        self.packet_send_immediately = 0
        self.packet_send_after_RREP = 0
        self.RERR_count = 0

    def sendMessage(self, id: str, message: str, sender: str):
        if id in self.nodes:
            self.nodes[id].receiveMessage(sender, message)

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
        self.RREP = []
        self.RERR = []
        self.TIMEOUT = 10
        self.timer = -1
        self.mnh = mnh
        self.input_buff = []
        self.coords = coords
        self.prev_coords = coords
        self.neighbour_timeout_arg = None

        # print("---------------------------")
        # print("node:", self.nodeId, " coordinates:", self.coords)
        # print("---------------------------")

        # print("-----------------------------------------")
        # print("Neighbours: ", self.neighbours)
        # print("-----------------------------------------")

        #sending mode
        if (nodeId == "A"):
            self.flag = "1"
        else:
            self.flag = "2"

    def receiveMessage(self, id: str, msg: str):
        self.input_buff.append([msg, id])

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
        source = [self.nodeId]
        dest_count = 1
        destSeq = destSeq+1
        RERR = ["RERR", source, dest_count, destId, destSeq]
        #broadcasting RERR to neighbours
        for x in self.neighbours:
            RERR = json.dumps(RERR)
            # self.sock.sendto(RERR, (neighbour_node[1], neighbour_node[2]))	
            self.mnh.sendMessage(x, RERR, self.nodeId)
            print(f"[RERR] {self.nodeId}->{x}")

    def neighbour_timeout(self, neigh_id):
        i = 0
        
        for x in self.routingTable:
            next_hop_id = x[1]
            if (neigh_id == next_hop_id):
                self.routingTable[i][5] = 0
            i+=1
        entry = self.getEntry(neigh_id)
        #destination and dest seq no
        if entry != None:
            self.sendRERR(neigh_id, entry[4])
            print("Timeout triggered for", neigh_id)
        self.showRoutingTable()

    def event_loop(self):
        self.timer = self.timer - 1

        if (self.timer == 0 and self.neighbour_timeout_arg != None):
            self.neighbour_timeout(self.neighbour_timeout_arg)
        #sending mode
        if (self.flag == "1"):
            # dest_id = "dawood"
            self.dest_id = random.choice([id for id, _ in self.mnh.nodes.items() if id != self.nodeId])
            #input("Name of destination node: ")
            #if it has destination route in its own table
            self.mnh.packet_created += 1
            if (self.checkRoutingTable(self.dest_id)):
                print("[LOG] I have active route to destination")
                print("[DATA] Sending message...")
                sender = [self.nodeId]
                receiver = self.dest_id
                message = f"[{self.nodeId}] Hello world!"
                data = json.dumps(["DATA",sender,receiver,message])

                # timer = Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(dest_id)[0]])
                # timer.start()
                # self.sock.sendto(data, tuple(self.getNextHop(dest_id)[1:]))

                self.timer = self.TIMEOUT
                self.neighbour_timeout_arg = self.getNextHop(self.dest_id)
                self.mnh.sendMessage(self.getNextHop(self.dest_id), data, self.nodeId)
                self.mnh.packet_send_immediately += 1
                self.showRoutingTable()
                self.flag = "2"
            else:
                print(f"[LOG] I don't have route to destination {self.dest_id}")
                print("[LOG] Let me discover the route.")
                #broadcasting RREQ to neighbours
                for x in self.neighbours:
                    # neighbour_node = self.neighbours.get(ns[x])
                    RREQ = ["RREQ", self.nodeId, self.seq_no, self.broadcast_no, self.dest_id, self.dest_seq, 0]
                    RREQ = json.dumps(RREQ)
                    # self.sock.sendto(RREQ, (neighbour_node[1], neighbour_node[2]))
                    self.mnh.sendMessage(x, RREQ, self.nodeId)	
                    print("[RREQ]", self.nodeId, "->", x)
                    self.flag = "2"
                
                self.mnh.RREQ_count += 1
                    
        #receiving mode
        elif (self.flag == "2"):
            while self.input_buff:
                msg,clientId = self.input_buff.pop(0)
                msg = json.loads(msg)
                #if it is RREQ packet
                self.showRoutingTable()
                if (msg[0] == "RREQ"):
                    print("[RREQ]",self.nodeId, "<-", clientId)
                    #if originator of RREQ is already in routing table or originator is receiving RREQ back to itself
                    if (self.getEntry(msg[1]) is not None or msg[1] == self.nodeId):
                        print(f"[DUP] {self.nodeId} Discarded RREQ from",  clientId)
                    else:
                        if (msg[1]!=self.nodeId):
                            #add reverse entry in routing table
                            self.routingTable.append([msg[1], clientId, msg[6]+1, self.life_time,msg[5],1])
                            print(f"Table update for {self.nodeId}: {self.routingTable[-1]}")
                            #serialize the routing table
                        
                        #if node has destination route in routing table
                        if (self.checkRoutingTable(msg[4])):
                            print("[LOG] I have active route to destination")
                            routeEntry = self.getEntry(msg[4])
                            dest_seq = self.seq_no	#RFC3561: 6.6.2	
                            RREP = ["RREP", routeEntry[0], dest_seq, msg[1], routeEntry[2], routeEntry[3]]
                            RREP = json.dumps(RREP)
                            
                            # self.sock.sendto(RREP, tuple(self.getNextHop(msg[1][0])[1:]))
                            self.mnh.sendMessage(self.getNextHop(msg[1]), RREP, self.nodeId)
                            print("[RREP]", self.nodeId, "->", msg[1])
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
                                self.mnh.sendMessage(self.getNextHop(msg[1]), RREP, self.nodeId)
                                print("[RREP]", self.nodeId, "->", self.getNextHop(msg[1]))
                            else:
                                print(f"[LOG] I don't have route to destination {destination} from RREQ")
                                print("[LOG] Let me discover the route.")
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
                                    self.mnh.sendMessage(x, RREQ, self.nodeId)
                                    print("[RREQ]", self.nodeId,"->", x)

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
                        print("[DATA] Sending message...")
                        sender = self.nodeId
                        receiver = self.dest_id
                        message = f"[{self.nodeId}] Hello World!"
                        #serialize data list into json
                        data = json.dumps(["DATA",sender,receiver,message])
                        # timer = Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(dest_id)[0]])
                        # timer.start()

                        self.timer = self.TIMEOUT
                        self.neighbour_timeout_arg = self.getNextHop(self.dest_id)

                        # self.sock.sendto(data, tuple(self.getNextHop(dest_id)[1:]))
                        self.mnh.sendMessage(self.getNextHop(self.dest_id), data, self.nodeId)
                        self.mnh.packet_send_after_RREP += 1
                        self.showRoutingTable()
                    else:
                        #hop count incrementing
                        msg[4] = msg[4]+1		
                        #serializing msg into json
                        RREP = json.dumps(msg)
                        #send data to Next_hop that leads to destination
                        # self.sock.sendto(RREP, tuple(self.getNextHop(msg[3][0])[1:]))
                        self.mnh.sendMessage(self.getNextHop(msg[3]), RREP, self.nodeId)
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
                        self.mnh.sendMessage(self.getNextHop(destination), data, self.nodeId)
                    #if data packet is received at intermediate node (not at destination)
                    else:
                        if (self.checkRoutingTable(msg[2])):
                            # timer.cancel()
                            # timer = Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(msg[2])[0]])
                            # timer.start()
                            self.timer = self.TIMEOUT
                            self.neighbour_timeout_arg = self.getNextHop(msg[2])

                            # print that forwarding message to next hop
                            print(f"[LOG] forwarding message to {self.getNextHop(msg[2])}")
                            data = json.dumps(msg)
                            # self.sock.sendto(data, tuple(self.getNextHop(msg[2])[0]))
                            self.mnh.sendMessage(self.getNextHop(msg[2]), data, self.nodeId)
                        else:
                            self.sendRERR(msg[2], -1)
                            
                #if it is REPLYDATA packet
                elif (msg[0] == "REPLYDATA"):
                    #if packet is received at destination
                    destination_id = msg[2]
                    if (destination_id == self.nodeId):
                        # timer.cancel()
                        self.timer = -1
                        print(msg[3])
                    #if packet is at intermediate node, forward it to next hop
                    else:
                        # timer.cancel()
                        # timer = Timer(self.TIMEOUT, self.neighbour_timeout, [self.getNextHop(destination_id)[0]])
                        # timer.start()

                        self.timer = self.TIMEOUT
                        self.neighbour_timeout_arg = self.getNextHop(destination_id)

                        print("[LOG] forwarding message to", self.getNextHop(destination_id))
                        data = json.dumps(msg)
                        # self.sock.sendto(data, tuple(self.getNextHop(destination_id)[1:]))
                        self.mnh.sendMessage(self.getNextHop(destination_id), data, self.nodeId)

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


