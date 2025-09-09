import numpy as np
import time
from pythonosc.udp_client import SimpleUDPClient
UDP_IP = "127.0.0.1"
UDP_PORT = 12000

# FORMAT
# chords_message = [[Chord, timestamp]]
# strum_message = [["DOWN"/"UP"], timestamp]
# pluck_message = [[note (midi value), duration, speed, slide_toggle, timestamp]]

# chords_message = [["A", 0.0], ["D", 4.0], ["E", 5.0], ["A", 6.0], ["On", 8.0]] # Marcus Demo 3/6/2025
# strum_message = [ ["DOWN", 1.0], ["UP", 2.0], ["DOWN", 4.0], ["UP", 5.0], ["DOWN", 6.0]] # Marcus Demo 3/6/2025
# pluck_message = [[45, .1, 10, 1], [47, .5, 10, 2], [48, 3, 4, 3], ] # Marcus Demo 3/6/2025

# pluck_message = [[45, 1, 10, 1],[51, 1, 4, 1.5], [45, 1, 5, 3], [51, 1, 8, 3.5], [45, 1, 5, 5.0], [51, 1.5, 8, 5.5],
#                 [45, 1, 10, 7],[51, 1, 4, 7.5], [45, 1, 5, 9], [51, 1, 8, 9.5], [45, 1, 5, 11], [51, 1.5, 8, 11.5],
#                 [45, 1, 10, 13],[51, 1, 4, 13.5], [45, 1, 5, 15], [51, 1, 8, 15.5], [45, 1, 5, 17], [51, 1.5, 8, 17.5]]

# pluck_message = [[40, 5, 10, 1], [51, 5, 10, 2], [56, 5, 10, 3]]

# pluck_message = [[56, 1, 2, 5]]
# Final Countdown
# chords_message = [["On", 3.0]]
# chords_message = [["F#m", 1.0], ["D", 2.0], ["Bm", 4.0], ["E", 6.0], ["Fdim7", 7.0],["F#m", 8.0], ["D", 10.0], ["Bm", 12.0], ["On", 14.0]]
# strum_message =  [["UP", 0.0], ["UP", 2.0], ["DOWN", 4.0], ["UP", 6.0], ["DOWN", 7.0], ["UP", 8.0], ["DOWN", 10.0], ["UP", 12.0]]
# pluck_message =  [[59, 1, 10, 0]]

# Testing Sliding
# chords_message = [["On", 12]]
# strum_message =  [["UP", 0]]
# # pluck_message = [[55, 1, 10, 0]]
# pluck_message = [[59, 4, 10, 1], [65, 4, 10, 3.5], [63, 4, 10, 6], [67, 4, 10, 8.5], [63, 4, 10, 11]]

# Testing Sliding Toggle. [midi_note, duration, speed, slide_toggle, timestamp]. Slide = 1, no slide = 0
# chords_message = [["On", 12]]
# strum_message =  [["UP", 0]]
# # SLIDES:
# pluck_message = [[59, 1, 7, 1, 1], [60, 1, 7, 1, 2], [61, 1, 7, 1, 3], [62, 1, 7, 1, 4], [63, 1, 7, 1, 5], [64, 1, 7, 1, 6], [65, 1, 7, 1, 7], [66, 7, 7, 1, 8], [67, 1, 7, 1, 9], [50, 1, 7, 1, 1], [51, 1, 7, 1, 2], [52, 1, 7, 1, 3], [53, 1, 7, 1, 4], [54, 1, 7, 1, 5], [55, 1, 7, 1, 6], [56, 1, 7, 1, 7], [57, 7, 7, 1, 8], [58, 1, 7, 1, 9]]
# pluck_message = [[50, 1, 7, 1, 1], [51, 1, 7, 1, 2], [52, 1, 7, 1, 3], [53, 1, 7, 1, 4], [54, 1, 7, 1, 5], [55, 1, 7, 1, 6], [56, 1, 7, 1, 7], [57, 7, 7, 1, 8], [58, 1, 7, 1, 9]]

# REGULAR NOTE CHANGES
# pluck_message = [[59, 4, 10, 1, 1], [65, 4, 10, 1, 3.5], [63, 4, 10, 1, 6], [67, 4, 10, 1, 8.5], [63, 4, 10, 1, 11]]

# chords_message = [["On", 50]]
# strum_message =  [["UP", 0]]
# pluck_message = [[40, 0.1, 10, 0, 1], [40, 0.1, 10, 0, 5], [40, 0.1, 10, 0, 10], [40, 0.1, 10, 0, 15], [40, 0.1, 10, 0, 20], [40, 0.1, 10, 0, 25], [40, 0.1, 10, 0, 30], [40, 0.1, 10, 0, 35], [40, 0.1, 10, 0, 40], [40, 0.1, 10, 0, 45]]

#
# chords_message_2 = [["On", 2]]
# pluck_message_2 = [[65, .5, 10, 3]]
# strum_message_2 =  [["UP", 2.3], ["DOWN", 2]]
#Two plucker Derrick Demo
# pluck_message = [[60, 1, 1, 1], [60, 1, 2, 2], [60, 1, 3, 3], [60, 1, 4, 4], [60, 1, 5, 5], [60, 1, 6, 6], [60, 1, 7, 7], [60, 1, 8, 8], [60, 1, 9, 9], [60, 1, 10, 10]]
# pluck_message = [[50, 10, 7, 1]]
# pluck_message = [[54, 2, 7, 1], [62, 2, 7, 1], [52, 0.3, 7, 2], [60, 0.3, 7, 2], [53, 2, 7, 2.5], [61, 2, 7, 2.5]]
# pluck_message = [[53, 0.5, 7, 1], [64, 0.5, 7, 1], [53, 0.3, 7, 1.8], [64, 0.3, 7, 2.05], [51, 0.5, 7, 2.5], [62, 0.5, 7, 2.5], [52, 0.5, 7, 2.9], [63, 0.5, 7, 2.9]]
# pluck_message = [[53, 0.3, 7, 1]]
# Ryan Demo, two phrase

# chords_message = [["On", 25]]
# chords_message_2 = [["On", 32]]
# strum_message =  [["UP", 0.0]]
# strum_message_2 =  [["UP", 0.0]]
# pluck_message =[
#         [50, 1, 5, 0],
#         [55, 0.5, 2, .5],
#         [62, 1.0, 4, 1.0],
#         [67, 0.5, 6, 2.0],
#         [59, 0.5, 5, 2.5],
#         [55, 0.5, 4, 3.0],
#         [50, 0.5, 2, 3.5],
#         [60, 0.5, 4, 4.0],
#         [67, 1.5, 6, 4.5],
#         [60, 0.5, 6, 6.0],
#         [55, 0.5, 4, 6.5],
#         [60, 0.5, 5, 7.0],
#         [55, 1.0, 4, 7.5],
#         [59, 1.5, 4, 8.5],
#         [50, 1.0, 2, 10.0],
#         [57, 0.5, 3, 11.0],
#         [50, 2.0, 2, 11.5],
#         [62, 1.5, 4, 13.5],
#         [50, 0.5, 2, 15.0],
#         [55, 0.5, 2, 15.5],
#         [60, 0.5, 4, 16.0],
#         [57, 2.5, 4, 16.5],
#         [60, 0.5, 5, 19.0],
#         [64, 0.5, 6, 19.5],
#         [62, 1.0, 6, 20.0],
#         [57, 0.5, 5, 21.0],
#         [62, 0.5, 6, 21.5],
#         [50, 0.5, 3, 22.0],
#         [57, 1.0, 3, 22.5],
#         [62, 0.5, 5, 23.5],
#         [55, 1.0, 4, 24.0],
#         [59, 0.5, 4, 25.0],
#         [55, 0.5, 3, 25.5],
#         [52, 0.5, 2, 26.0],
#         [55, 0.5, 2, 26.5],
#         [52, 1.0, 2, 27.0],
#         [66, 1.0, 5, 28.0],
#         [62, 0.5, 6, 29.0],
#         [66, 0.5, 7, 29.5],
#         [64, 1.0, 7, 30.0],
#         [52, 0.5, 4, 31.0]]
#
#         # Second Message
# pluck_message_2 = [[50, 0.5, 1, 0],
#         [59, 0.5, 3, 0.5],
#         [62, 1.0, 5, 1.0],
#         [55, 0.5, 4, 2.0],
#         [67, 0.5, 6, 2.5],
#         [55, 0.5, 4, 3.0],
#         [59, 0.5, 4, 3.5],
#         [60, 0.5, 5, 4.0],
#         [67, 1.5, 7, 4.5],
#         [60, 1.5, 6, 6.0],
#         [64, 1.0, 7, 7.5],
#         [67, 1.5, 8, 8.5],
#         [50, 1.0, 4, 10.0],
#         [57, 0.5, 4, 11.0],
#         [50, 0.5, 2, 11.5],
#         [62, 0.5, 4, 12.0],
#         [50, 1.0, 2, 12.5],
#         [55, 1.0, 2, 13.5],
#         [62, 0.5, 4, 14.5],
#         [55, 1.0, 3, 15.0],
#         [57, 1.5, 3, 16.0],
#         [52, 0.5, 2, 17.5],
#         [64, 0.5, 5, 18.0],
#         [60, 0.5, 5, 18.5],
#         [57, 0.5, 4, 19.0],
#         [52, 0.5, 3, 19.5],
#         [57, 1.0, 3, 20.0],
#         [66, 0.5, 6, 21.0],
#         [62, 0.5, 6, 21.5],
#         [57, 0.5, 5, 22.0],
#         [62, 1.5, 6, 22.5],
#         [55, 1.0, 4, 24.0],
#         [54, 0.5, 3, 25.0],
#         [55, 0.5, 3, 25.5],
#         [59, 1.0, 4, 26.0],
#         [52, 0.5, 3, 27.0],
#         [59, 0.5, 4, 27.5],
#         [57, 0.5, 4, 28.0],
#         [50, 0.5, 2, 28.5],
#         [57, 0.5, 3, 29.0],
#         [50, 0.5, 2, 29.5],
#         [60, 1.0, 4, 30.0],
#         [64, 0.5, 6, 31.0]]

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

# MARCUS DEMOS POSTER DAY
# 1. Pluck Speeds
chords_message = [["On", 8]]
# strum_message =  [["UP", 0]]
# # E
# pluck_message = [[42, 2, 1, 0, 1], [46, 2, 10, 0, 4]]

# D
# pluck_message = [[50, 2, 1, 0, 1], [52, 2, 10, 0, 4]]

# B
# pluck_message = [[59, 2, 1, 0, 1], [61, 2, 10, 0, 4]]

# 2. Glissando Multiple Strings
chords_message = [["On", 9]]
# # strum_message =  [["UP", 0]]
pluck_message = [
 #                [59, 3, 7, 0, 1], [61, 3, 7, 0, 3], [63, 3, 7, 0, 5], [65, 2, 7, 0, 7],
                 [50, 3, 7, 0, 1], [52, 3, 7, 0, 3], [54, 3, 7, 0, 5], [56, 2, 7, 0, 7]
 #              [40, 3, 7, 0, 1], [42, 3, 7, 0, 3], [44, 3, 7, 0, 5], [46, 2, 7, 0, 7]
                ]

# # 3. Short Song
# , ["Dsus2", 5],["Cmaj7", 9],  ["Am", 13], ["On", 17]
# chords_message = [["On", 0]]
# strum_message =  [["UP", 0]]
# pluck_message = [[50, .5, 10, 0, 1.5], [50, .1, 1, 0, 2.5], [50, .1, 1, 0, 3],
#                  [50, .5, 10, 0, 3.5], [50, .1, 1, 0, 4.5], [50, .1, 1, 0, 5],
#                  [54, .5, 10, 0, 5.5], [54, .1, 1, 0, 6.5], [54, .1, 1, 0, 7],
#                  [54, .5, 10, 0, 7.5], [54, .1, 1, 0, 8.5], [54, .1, 1, 0, 9],
#                  [50, .5, 10, 0, 9.5], [50, .1, 1, 0, 10.5], [50, .1, 1, 0, 11],
#                  [52, .5, 10, 0, 11.5], [52, .1, 1, 0, 12.5], [52, .1, 1, 0, 13],
#                  [54, .5, 10, 0, 13.5], [54, .1, 1, 0, 14.5], [54, .1, 1, 0, 15],
#                  [54, .5, 10, 0, 15.5], [54, .1, 1, 0, 16.5], [54, .1, 1, 0, 17],
#                  # String seperator
#                  [62, .5, 10, 0, 1.5], [62, .6, 5, 0, 2], [62, 3, 5, 0, 3],
#                  [66, 1, 10, 1, 5.2], [66, .6, 2, 1, 6.5], [66, .6, 2, 1, 7.5],
#                  [62, .5, 1, 0, 9.5], [62, .6, 1, 0, 10.5], [62, 1, 10, 0, 11.5],
#                  [66, 1, 10, 1, 13], [66, .6, 2, 1, 14], [66, .6, 2, 1, 15]]
#
# chords_message_2 = [["On", 11]]
# strum_message_2 = [["UP", 0.0]]
# pluck_message_2 = [[64, 1, 10, 0, 0], [55, 1, 10, 0, 0],
#                    # Phrase Smoothing
#                    [64, 2, 10, 0, .5], [67, 2, 5, 1, 2], [66, 1.5, 5, 0, 3],
#                    [64, 1, 5, 0, 5], [62, 1, 5, 0, 7], [62, 1, 5, 0, 8], [62, .6, 10, 0, 10],
#                    # String Seperator
#                    [55, 2, 10, 0, .5], [52, 2, 5, 1, 2], [54, 2, 2, 0, 4],
#                    [55, .5, 10, 1, 6], [50, 2, 3, 1, 7], [50, 1.5, 5, 0, 9]]

# chords_message = [["On", 0]]
# strum_message = [["UP", 0.0]]
# pluck_message = [[59, 1, 10, 0, 2]]  # Pressing start on one of the strings in the UI will interpolate one tremolo and keep appending it until a stop message is received
#
# chords_message_2 = [["On", 4]]
# strum_message_2 = [["UP", 0.0]]
# pluck_message_2 = [[59, 1, 10, 0, 0]]

# Test Audio
# chords_message = [["On", 10]]
# strum_message = [["UP", 0.0]]
# pluck_message = [[50, 10, 10, 0, 1]]
# pluck_message = [[50, 0.1, 1, 0, 0], [50, 0.1, 1, 0, 5], [50, 0.1, 1, 0, 10], [50, 0.1, 1, 0, 15], [50, 0.1, 1, 0, 20], [50, 0.1, 1, 0, 25], [50, 0.1, 1, 0, 30], [50, 0.1, 1, 0, 35], [50, 0.1, 1, 0, 40], [50, 0.1, 1, 0, 45]]

def send_osc_message(client, address, data):
    print(f"Sending OSC message to {address}: {data}")
    client.send_message(address, data)

def main():
    # Create an OSC client
    client = SimpleUDPClient(UDP_IP, UDP_PORT)
    send_osc_message(client, "/Chords", chords_message)
    # send_osc_message(client, "/Strum", strum_message)
    # pluck_message = create_tremolo_message()
    send_osc_message(client, "/Pluck", pluck_message)
    time.sleep(1)
    # send_osc_message(client, "/Chords", chords_message_2)
    # send_osc_message(client, "/Strum", strum_message_2)
    # # # pluck_message = create_tremolo_message()
    # send_osc_message(client, "/Pluck", pluck_message_2)
    # # time.sleep(1)

    # send_osc_message(client, "/Chords", chords_message_2)
    # send_osc_message(client, "/Strum", strum_message_2)
    # send_osc_message(client, "/Pluck", pluck_message_2)

    counter = 0

    # while counter < 5:
    #     send_osc_message(client, "/Chords", chords_message)
    #     send_osc_message(client, "/Strum", strum_message)
    #     send_osc_message(client, "/Pluck", pluck_message)
    #     counter += 1
    #     time.sleep(1)


if __name__ == "__main__":
    main()