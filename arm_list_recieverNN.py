import threading
import queue
import time
from pythonosc import dispatcher
from pythonosc import osc_server
import RobotController
from UI.messaging.udp_definitions import *
from parsing.ArmListParser import ArmListParser

OSC_IP = "127.0.0.1"
OSC_PORT = 12000

message_queue = queue.SimpleQueue()

def handle_message(address, *args):
    message_type = address.strip("/")
    message_queue.put((message_type, args))
    print(f"Received {message_type}: {args}")

def process_messages():
    chords = strum = pluck = None
    while True:
        try:
            while not message_queue.empty():
                message_type, data = message_queue.get_nowait()
                if message_type == "Chords":
                    chords = data
                elif message_type == "Strum":
                    strum = data
                elif message_type == "Pluck":
                    pluck = data

                if chords and strum and pluck:
                    song_trajectories_dict = ArmListParser.parseAllMIDI(chords, strum)
                    song_trajectories_list = [value for value in song_trajectories_dict.values()]
                    RobotController.main(song_trajectories_list)
                    chords = strum = pluck = None
        except queue.Empty:
            pass
        time.sleep(0.001)

def start_osc_server():
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(handle_message)
    server = osc_server.ThreadingOSCUDPServer((OSC_IP, OSC_PORT), disp)
    print(f"OSC Server listening on {server.server_address}")
    server.serve_forever()

if __name__ == "__main__":
    osc_thread = threading.Thread(target=start_osc_server)
    osc_thread.start()

    process_thread = threading.Thread(target=process_messages)
    process_thread.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped.")