from pythonosc.udp_client import SimpleUDPClient
# Local Device
UDP_IP = "127.0.0.1"
UDP_PORT = 12000

# FORMAT
# Chords = [[Chord, timestamp]]
# strum message = [["DOWN"/"UP"], timestamp]

chords_message = [["C", 0.0], ["G", 1.0], ["A", 2.0], ["F", 3.0]]
strum_message = [["DOWN", 0.0], ["UP", 1.0], ["DOWN", 2.0], ["UP", 3.0]]
# pluck_message = [[]]

def send_osc_message(client, address, data):
    print(f"Sending OSC message to {address}: {data}")
    client.send_message(address, data)

def main():
    # Create an OSC client
    client = SimpleUDPClient(UDP_IP, UDP_PORT)
    send_osc_message(client, "/Chords", chords_message)
    send_osc_message(client, "/Strum", strum_message)
    # send_osc_message(client, "/Pluck", pluck_message)


if __name__ == "__main__":
    main()