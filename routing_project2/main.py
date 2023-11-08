import time
import PySimpleGUI as sg

from aodv import *

GRAP_WIDTH = 500
GRAPH_HEIGHT = 500

NODE_COORD_WIDTH = 100
NODE_COORD_HEIGHT = 100

LABEL_MOD_X = 0
LABEL_MOD_Y = 0
LABEL_SIZE = 9
#max send/receive range of nodes
MAX_RANGE = 20
NUM_NODES = 20
STEP_SIZE = 10

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

def reset_sim(window: sg.Window, nodes):
    running = False
    run_step = 0
    mnh = MainNodeHandler(nodes)
    dots = draw_nodes(window, mnh.nodes)
    print("Reset!")

    return running, run_step, mnh, dots


def main_gui():
    """
    Main function for the UI of the program.
    Creates the window and acts accordingly on mouse clicks.
    """
    global MAX_RANGE
    global STEP_SIZE

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
                [sg.Text("Node step size: "), sg.InputText("2", enable_events=True, key="-NODE-STEPS-", size=(5, 1))],
                [sg.Text("Sim steps: "), sg.InputText("100", enable_events=True, key="-SIM-STEPS-", size=(5, 1))],

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
    sim_steps = 100
    run_step = 0
    dots = []

    # UI event loop. Acts on events (button presses etc...)
    while True:
        # Load events and values.
        event, values = window.read(timeout=20)

        if mnh == None:
            mnh = MainNodeHandler(nodes)
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
            running, run_step, mnh, dots = reset_sim(window, nodes)

        if event == "-NODES-" and values["-NODES-"].isdigit():
            nodes = int(values["-NODES-"])
            running, run_step, mnh, dots = reset_sim(window, nodes)
            print(f"Updated nodes to {nodes}")

        if event == "-RANGE-" and values["-RANGE-"].isdigit():
            MAX_RANGE = int(values["-RANGE-"])
            draw_nodes(window, mnh.nodes)
            print(f"Updated range to {MAX_RANGE}")

        if event == "-NODE-STEPS-" and values["-NODE-STEPS-"].isdigit():
            STEP_SIZE = int(values["-NODE-STEPS-"])
            print(f"Updated node step size to {STEP_SIZE}")

        if event == "-SIM-STEPS-" and values["-SIM-STEPS-"].isdigit():
            sim_steps = int(values["-SIM-STEPS-"])
            print(f"Updated sim steps to {sim_steps}")

        if running and run_step < sim_steps:
            run_step += 1
            # while (1):
            mnh.move_nodes(STEP_SIZE, NODE_COORD_WIDTH, NODE_COORD_HEIGHT)
            mnh.find_neighbours(MAX_RANGE)
            for _, n in mnh.nodes.items():
                n.event_loop()
            #  time.sleep(0.010)
            move_dots(window, dots, mnh.nodes)

        if run_step >= sim_steps:
            print("Finished!")
            print(f"RREQ send: {mnh.RREQ_count}")
            print(f"Total packets created: {mnh.packet_created}")
            print(f"Total packets send immediately: {mnh.packet_send_immediately}")
            print(f"Total packets send after RREP: {mnh.packet_send_after_RREP}")
            print(f"Total packets dropped, no route: {mnh.packet_created - mnh.packet_send_immediately - mnh.packet_send_after_RREP}")
            running, run_step, mnh, dots = reset_sim(window, nodes)

        window['-STEP-'].update(run_step)
        
            
    # When broken out of loop, close window
    window.close()

if __name__ == "__main__":

    main_gui()
