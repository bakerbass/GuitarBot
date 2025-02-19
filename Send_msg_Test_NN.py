from pythonosc.udp_client import SimpleUDPClient
UDP_IP = "127.0.0.1"
UDP_PORT = 12000

# FORMAT
# chords_message = [[Chord, timestamp]]
# strum_message = [["DOWN"/"UP"], timestamp]
# pluck_message = [[note (midi value), duration, timestamp]] (speed?) (duration = 0 is a pick)

#chords_message = [["C", 0.0], ["G", 1.0], ["A", 2.0], ["F", 3.0]]
chords_message = [["C", 0.0]]
#strum_message = [["DOWN", 0.0], ["UP", 1.0], ["DOWN", 2.0], ["UP", 3.0]]
strum_message = [["DOWN", 0.0]]
pluck_message = [[40, .05, 0.0], [45, .05, 0.09], [45, .05, 2.0],  [45, .05, 4.0],  [40, .025, 6.0],  [41, .05, 6.299]]

def send_osc_message(client, address, data):
    print(f"Sending OSC message to {address}: {data}")
    client.send_message(address, data)

def main():
    # Create an OSC client
    client = SimpleUDPClient(UDP_IP, UDP_PORT)
    send_osc_message(client, "/Chords", chords_message)
    send_osc_message(client, "/Strum", strum_message)
    send_osc_message(client, "/Pluck", pluck_message)


if __name__ == "__main__":
    main()