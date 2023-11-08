import time
import PySimpleGUI as sg

from aodv import *

GRAP_WIDTH = 500
GRAPH_HEIGHT = 500

NODE_COORD_WIDTH = 100
NODE_COORD_HEIGHT = 100

LABEL_MOD_X = 1
LABEL_MOD_Y = -1
LABEL_SIZE = 9

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
        label = window["-GRAPH-VIEW-"].draw_text(l, (gx+LABEL_MOD_X, gy+LABEL_MOD_Y), color="black", text_location=sg.TEXT_LOCATION_CENTER, font=("Arial", LABEL_SIZE))
        dots.append((dot, (x,y), label))

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
        graph.MoveFigure(dots[i][0], gx - gpx, gy - gpy)
        graph.MoveFigure(dots[i][2], gx - gpx+LABEL_MOD_X, gy - gpy+LABEL_MOD_Y)

def reset_sim(window: sg.Window):
    running = False
    run_step = 0
    mnh = MainNodeHandler()
    dots = draw_nodes(window, mnh.nodes)
    print("Reset!")

    return running, run_step, mnh, dots


def main_gui():
    """
    Main function for the UI of the program.
    Creates the window and acts accordingly on mouse clicks.
    """

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
    nodes = 10
    sim_steps = 100
    run_step = 0
    dots = []

    # UI event loop. Acts on events (button presses etc...)
    while True:
        # Load events and values.
        event, values = window.read(timeout=20)

        if mnh == None:
            mnh = MainNodeHandler()
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
            running, run_step, mnh, dots = reset_sim(window)

        if event == "-NODES-":
            nodes = values["-NODES-"]
            print(f"Updated nodes to {nodes}")

        if event == "-SIM-STEPS-":
            sim_steps = values["-SIM-STEPS-"]
            print(f"Updated sim steps to {sim_steps}")

        if running and run_step < sim_steps:
            run_step += 1
            # while (1):
            for _, n in mnh.nodes.items():
                n.event_loop()
            #  time.sleep(0.010)
            move_dots(window, dots, mnh.nodes)

        if run_step >= sim_steps:
            print("Finished!")
            running, run_step, mnh, dots = reset_sim(window)

        window['-STEP-'].update(run_step)
        
            
    # When broken out of loop, close window
    window.close()

if __name__ == "__main__":


    main_gui()
