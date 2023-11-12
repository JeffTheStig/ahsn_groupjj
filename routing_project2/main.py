import time
import PySimpleGUI as sg
import random

from aodv import *

GRAP_WIDTH = 500
GRAPH_HEIGHT = 500

NODE_COORD_WIDTH = 100
NODE_COORD_HEIGHT = 100

LABEL_MOD_X = 0
LABEL_MOD_Y = 0
LABEL_SIZE = 9
#max send/receive range of nodes
MAX_RANGE = 10
NUM_NODES = 10
MOVEMENT_RANGE = 5
SEED = 2023

def normalize_graph_coords(x, y, w, h, invert_y = True):
    """
    Takes the coordinates and image width and height and normalizes the coordintes.
    Inverts y is invert_y is set to True. Defaults to True

    :param x: The x-coordinate to normalize
    :param y: The y-coordinate to normalize
    :param w: Width of the image from which the coordinates came
    :param h: Heigth of the image from which the coordinates came
    :param invert_y: If y should be inverted (if y=0 is the bottom, but should become the top in the normalized coordinates)
    """
    if invert_y:
        y = h - y
    x = x / w
    y = y / h

    return x,y

def draw_nodes(window: sg.Window, nodes: list):
    window["-GRAPH-VIEW-"].erase()

    dots = []

    for l, n in nodes.items():
        x, y = n.coords
        gx, gy = normalize_graph_coords(x, y, NODE_COORD_WIDTH, NODE_COORD_HEIGHT, True)
        gx = gx * GRAP_WIDTH
        gy = gy * GRAPH_HEIGHT
        dot = window["-GRAPH-VIEW-"].DrawCircle((gx, gy), 5, fill_color='red')
        r = window["-GRAPH-VIEW-"].DrawCircle((gx, gy), MAX_RANGE / NODE_COORD_WIDTH * GRAP_WIDTH, line_color='black')
        label = window["-GRAPH-VIEW-"].draw_text(l, (gx+LABEL_MOD_X, gy+LABEL_MOD_Y), color="black", text_location=sg.TEXT_LOCATION_CENTER, font=("Arial", LABEL_SIZE))
        dots.append((dot, (x,y), label, r))

    return dots

def move_dots(window: sg.Window, dots: list, nodes: list):
    graph = window["-GRAPH-VIEW-"]
    for i, (_, n) in enumerate(nodes.items()):
        x, y = n.coords
        px, py = n.prev_coords
        gx, gy = normalize_graph_coords(x, y, NODE_COORD_WIDTH, NODE_COORD_HEIGHT, True)
        gx = gx * GRAP_WIDTH
        gy = gy * GRAPH_HEIGHT

        gpx, gpy = normalize_graph_coords(px, py, NODE_COORD_WIDTH, NODE_COORD_HEIGHT, True)
        gpx = gpx * GRAP_WIDTH
        gpy = gpy * GRAPH_HEIGHT
        graph.MoveFigure(dots[i][0], gx - gpx, gy - gpy) # Dot
        graph.MoveFigure(dots[i][3], gx - gpx, gy - gpy) # Range
        graph.MoveFigure(dots[i][2], gx - gpx+LABEL_MOD_X, gy - gpy+LABEL_MOD_Y) # Label

def reset_sim(window: sg.Window, nodes, seed):
    running = False
    run_step = 0
    mnh = MainNodeHandler(nodes, seed)
    dots = draw_nodes(window, mnh.nodes)
    print("Reset!")

    return running, run_step, mnh, dots


def main_gui():
    """
    Main function for the UI of the program.
    Creates the window and acts accordingly on mouse clicks.
    """
    global MAX_RANGE
    global MOVEMENT_RANGE

    # Total layout of the program. Also adds a terminal output window.
    layout = [
        [
            sg.Column([[sg.Graph((GRAP_WIDTH, GRAPH_HEIGHT), (0, 0), (GRAP_WIDTH, GRAPH_HEIGHT), enable_events=True, key='-GRAPH-VIEW-', background_color='grey')]]),
            sg.Column([[sg.Text("Current step:"), sg.Text("0", key="-STEP-")]])
        ],
        [sg.HSeparator()],
        [
            sg.Column([
                [sg.Button("Start", key="-START-")],
                [sg.Button("Pause", key="-PAUSE-")],
                [sg.Button("Reset", key="-RESET-")],
                [sg.HSeparator()],
                [sg.Text("Nodes: "), sg.InputText("10", enable_events=True, key="-NODES-", size=(5, 1))],
                [sg.Text("Node range: "), sg.InputText("10", enable_events=True, key="-RANGE-", size=(5, 1))],
                [sg.Text("Node movement range: "), sg.InputText("5", enable_events=True, key="-MOVEMENT-RANGE-", size=(5, 1))],
                [sg.Text("Sim steps: "), sg.InputText("100", enable_events=True, key="-SIM-STEPS-", size=(5, 1))],
                [sg.Text("Seed: "), sg.InputText("2023", enable_events=True, key="-SEED-", size=(5, 1))],
                [sg.Text("Packets to send: "), sg.InputText("10", enable_events=True, key="-SEND-", size=(5, 1))],
                [   
                    sg.Text("Protocol selection: "),
                    sg.Radio("AODV", "protocol", enable_events=True, size=(10,1), key="-AODV-", default=True),
                    sg.Radio("DSR", "protocol", enable_events=True, size=(10,1), key="-DSR-")
                ],

            ]),
            sg.VSeperator(),
            sg.Column([[sg.Output(size=(180,20), echo_stdout_stderr=True, key="-TERMINAL-")]])   
        ]
    ]

    # Create the window.
    window = sg.Window("AODV simulator", layout)

    mnh = None
    running = False
    nodes = NUM_NODES
    seed = SEED
    sim_steps = 100
    run_step = 0
    dots = []
    dsr = False
    packets_to_send = 10

    # UI event loop. Acts on events (button presses etc...)
    while True:
        # Load events and values.
        event, values = window.read(timeout=20)

        if mnh == None:
            mnh = MainNodeHandler(nodes, seed)
            dots = draw_nodes(window, mnh.nodes)

        # Close if event is exit.
        if event == "Exit" or event == sg.WINDOW_CLOSED:
            break

        # Events to load the images.
        # Load the image from the path given in the path field (hidden) and display it.
        if event == "-START-":
            running = True

        if event == "-PAUSE-":
            running = False

        if event == "-RESET-":
            running, run_step, mnh, dots = reset_sim(window, nodes, seed)

        if event == "-NODES-" and values["-NODES-"].isdigit():
            nodes = int(values["-NODES-"])
            running, run_step, mnh, dots = reset_sim(window, nodes, seed)
            print(f"Updated nodes to {nodes}")

        if event == "-RANGE-" and values["-RANGE-"].isdigit():
            MAX_RANGE = int(values["-RANGE-"])
            draw_nodes(window, mnh.nodes)
            print(f"Updated range to {MAX_RANGE}")

        if event == "-MOVEMENT-RANGE-" and values["-MOVEMENT-RANGE-"].isdigit():
            MOVEMENT_RANGE = int(values["-MOVEMENT-RANGE-"])
            print(f"Updated node movement range to {MOVEMENT_RANGE}")

        if event == "-SIM-STEPS-" and values["-SIM-STEPS-"].isdigit():
            sim_steps = int(values["-SIM-STEPS-"])
            print(f"Updated sim steps to {sim_steps}")

        if event == "-SEED-" and values["-SEED-"].isdigit():
            seed = int(values["-SEED-"])
            running, run_step, mnh, dots = reset_sim(window, nodes, seed)
            print(f"Updated seed to {seed}")

        if event == "-SEND-" and values["-SEND-"].isdigit():
            packets_to_send = int(values["-SEND-"])
            print(f"Updated packet to send to {packets_to_send}")

        if event == "-AODV-":
            dsr = False
            mnh.dsr = dsr
            print(f"Set protocol to AODV (dsr={dsr})")

        if event == "-DSR-":
            dsr = True
            mnh.dsr = dsr
            print(f"Set protocol to DSR (dsr={dsr})")

        if running and run_step < sim_steps:
            run_step += 1
            # while (1):
            mnh.move_nodes(MOVEMENT_RANGE, NODE_COORD_WIDTH, NODE_COORD_HEIGHT)
            move_dots(window, dots, mnh.nodes)
            mnh.find_neighbours(MAX_RANGE)
            if run_step % int((sim_steps / packets_to_send) + 1) == 0:
                sender_node = random.choice([id for id, n in mnh.nodes.items() if n.flag == "2" and not n.replying])
                print(f"[MAIN] Node {sender_node} created package")
                mnh.nodes[sender_node].flag = "0" # Set the node in sending mode.
                mnh.packets_created_main += 1
            for _, n in mnh.nodes.items():
                n.event_loop(run_step)
            #  time.sleep(0.010)

        if run_step >= sim_steps:
            print("Finished!")
            print(f"RREQ send: {mnh.RREQ_count}")
            print(f"Total packets created: {mnh.packet_created}")
            print(f"Total packets send immediately: {mnh.packet_send - mnh.packet_send_after_RREP}")
            print(f"Total packets send after RREP: {mnh.packet_send_after_RREP}")
            print(f"Total packets dropped, no route: {mnh.packet_created - mnh.packet_send}")
            print()
            print(f"Forwarded RouteRequests (node did not have route either): {mnh.RREQ_forwards}")
            print(f"Amount of forwards for all data packets: {mnh.packet_forwards}")
            print(f"Amount of times a timeout was triggered (path not found or responding: {mnh.timer_timeouts}")
            print(f"Amount of path traversals that where broken: {mnh.broken_paths}")
            print(f"Amount of times route was found in RoutingTable on intermediate node: {mnh.RREP_after_in_rt}")
            print(f"Timeouts due to TTL on DSR: {mnh.TTL_timouts}")
            print()
            print(f"Total delay / discovery time (steps): {mnh.packet_delay_steps}")
            print(f"Avg delay (steps): {mnh.packet_delay_steps / mnh.packet_send}") if mnh.packet_send > 0 else print(f"Avg delay (steps): 0")
            print(f"Avg discovery time (steps): {mnh.packet_delay_steps / mnh.packet_send_after_RREP}") if mnh.packet_send_after_RREP > 0 else print(f"Avg discovery time (steps): 0")
            print(f"Total delay / discovery time (s): {mnh.packet_delay_s}")
            print(f"Avg delay (s): {mnh.packet_delay_s / mnh.packet_send}") if mnh.packet_send > 0 else print(f"Avg delay (s): 0")
            print(f"Avg discovery time (s): {mnh.packet_delay_s / mnh.packet_send_after_RREP}") if mnh.packet_send_after_RREP > 0 else print(f"Avg discovery time (s): 0")
            print()
            print(f"RREQ send: {mnh.RREQ_send}")
            print(f"RREP send: {mnh.RREP_send}")
            print(f"RERR send: {mnh.RERR_send}")
            print(f"packet send: {mnh.packet_send}")
            print(f"reply send: {mnh.reply_send}")
            print(f"Packets arrived: ", mnh.packet_arrived)
            print(f"Replies arrived: ", mnh.reply_arrived)
            total_packets = mnh.RREQ_send + mnh.RREP_send + mnh.RERR_send + mnh.packet_send + mnh.reply_send
            route_packets = mnh.RREQ_send + mnh.RREP_send + mnh.RERR_send
            print(f"Routing overhead % : {route_packets / total_packets * 100}")

            table_entries = 0
            for _, n in mnh.nodes.items():
                for entry in n.routingTable:
                    table_entries += 1
            print(f"Total routing entries: {table_entries}")
            print(f"Average routing table size: {table_entries / nodes}")
            print()
            print(f"packets_created_main: {mnh.packets_created_main}")

            running, run_step, mnh, dots = reset_sim(window, nodes, seed)

        window['-STEP-'].update(run_step)
        
            
    # When broken out of loop, close window
    window.close()

if __name__ == "__main__":

    main_gui()
