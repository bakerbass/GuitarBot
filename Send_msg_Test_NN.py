import numpy as np
from pythonosc.udp_client import SimpleUDPClient
UDP_IP = "127.0.0.1"
UDP_PORT = 12000

# FORMAT
# chords_message = [[Chord, timestamp]]
# strum_message = [["DOWN"/"UP"], timestamp]
# pluck_message = [[note (midi value), duration, speed, timestamp]]

# chords_message = [["A", 0.0], ["D", 4.0], ["E", 5.0], ["A", 6.0], ["On", 8.0]] # Marcus Demo 3/6/2025
# strum_message = [ ["DOWN", 1.0], ["UP", 2.0], ["DOWN", 4.0], ["UP", 5.0], ["DOWN", 6.0]] # Marcus Demo 3/6/2025
# pluck_message = [[45, .1, 10, 1], [47, .5, 10, 2], [48, 3, 4, 3], ] # Marcus Demo 3/6/2025

# pluck_message = [[45, 1, 10, 1],[51, 1, 4, 1.5], [45, 1, 5, 3], [51, 1, 8, 3.5], [45, 1, 5, 5.0], [51, 1.5, 8, 5.5],
#                 [45, 1, 10, 7],[51, 1, 4, 7.5], [45, 1, 5, 9], [51, 1, 8, 9.5], [45, 1, 5, 11], [51, 1.5, 8, 11.5],
#                 [45, 1, 10, 13],[51, 1, 4, 13.5], [45, 1, 5, 15], [51, 1, 8, 15.5], [45, 1, 5, 17], [51, 1.5, 8, 17.5]]

# pluck_message = [[40, 5, 10, 1], [51, 5, 10, 2], [56, 5, 10, 3]]

# pluck_message = [[56, 1, 2, 5]]

# chords_message = [["F#m", 0.0], ["D", 2.0], ["Bm", 4.0], ["E", 6.0], ["Fdim7", 7.0],["F#m", 8.0], ["D", 10.0], ["Bm", 12.0], ["On", 14.0]]
# strum_message =  [["DOWN", 0.0],["UP", 2.0],["DOWN", 4.0], ["UP", 6.0], ["DOWN", 7.0], ["UP", 8.0], ["DOWN", 10.0], ["UP", 12.0]]
# pluck_message =  [[52, 1, 5, 1]]
# Ryan Demo

chords_message = [["On", 2.0]]
strum_message =  [["UP", 0.0]]

pluck_message =[
        [50, 1, 1, 0]]
        # [55, 0.5, 2, .5],
        # [62, 1.0, 4, 1.0],
        # [67, 0.5, 6, 2.0],
        # [59, 0.5, 5, 2.5],
        # [55, 0.5, 4, 3.0],
        # [50, 0.5, 2, 3.5],
        # [60, 0.5, 4, 4.0],
        # [67, 1.5, 6, 4.5],
        # [60, 0.5, 6, 6.0],
        # [55, 0.5, 4, 6.5],
        # [60, 0.5, 5, 7.0],
        # [55, 1.0, 4, 7.5],
        # [59, 1.5, 4, 8.5],
        # [50, 1.0, 2, 10.0],
        # [57, 0.5, 3, 11.0],
        # [50, 2.0, 2, 11.5],
        # [62, 1.5, 4, 13.5],
        # [50, 0.5, 2, 15.0],
        # [55, 0.5, 2, 15.5],
        # [60, 0.5, 4, 16.0],
        # [57, 2.5, 4, 16.5],
        # [60, 0.5, 5, 19.0],
        # [64, 0.5, 6, 19.5],
        # [62, 1.0, 6, 20.0],
        # [57, 0.5, 5, 21.0],
        # [62, 0.5, 6, 21.5],
        # [50, 0.5, 3, 22.0],
        # [57, 1.0, 3, 22.5],
        # [62, 0.5, 5, 23.5],
        # [55, 1.0, 4, 24.0],
        # [59, 0.5, 4, 25.0],
        # [55, 0.5, 3, 25.5],
        # [52, 0.5, 2, 26.0],
        # [55, 0.5, 2, 26.5],
        # [52, 1.0, 2, 27.0],
        # [66, 1.0, 5, 28.0],
        # [62, 0.5, 6, 29.0],
        # [66, 0.5, 7, 29.5],
        # [64, 1.0, 7, 30.0],
        # [52, 0.5, 4, 31.0]]
# , [51, .1, 10, 2], [61, .1, 10, 3]
# Derrick Demo for 2/27/2025 -- Randomly generated three picker tremolos with amplitude scaling
def create_tremolo_message():
    #1. Generate 5 random speeds
    speeds = np.arange(1, 11)
    rand_speeds = speeds[np.random.choice(len(speeds), 5)]
    print(rand_speeds)

    #2. Generate 5 random MIDI values (for the 3 current strings)
    midi_notes = np.array([45, 51])
    rand_notes = midi_notes[np.random.choice(len(midi_notes), 5, replace=True)]
    print(rand_notes)

    #3. Generate 5 random durations
    durations = np.arange(1, 11)
    rand_durations = durations[np.random.choice(len(durations), 5)]
    print(rand_durations)

    # 3. Generate 5 random timestamps
    #timestamps = np.arange(1, 6)
    #rand_times = timestamps[np.random.choice(len(timestamps), 5)]
    #print(rand_times)

    np_messages = []
    for i in range(len(rand_speeds)):
        message = [rand_notes[i], rand_durations[i], rand_speeds[i], i+1]
        np_messages.append(message)

    pluck_messages = np.vstack(np_messages)
    return pluck_messages.tolist()

    
def send_osc_message(client, address, data):
    print(f"Sending OSC message to {address}: {data}")
    client.send_message(address, data)

def main():
    # Create an OSC client
    client = SimpleUDPClient(UDP_IP, UDP_PORT)
    send_osc_message(client, "/Chords", chords_message)
    send_osc_message(client, "/Strum", strum_message)
    # pluck_message = create_tremolo_message()
    send_osc_message(client, "/Pluck", pluck_message)


if __name__ == "__main__":
    main()