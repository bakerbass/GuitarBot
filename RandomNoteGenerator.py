# Generates Random Notes in C for GuitarBot to play

import numpy as np
# 1. Set string min and max midi values
# 2. Random amount of note changes per string (3 to 6) Random amount of string speeds per string (3 to 6)
# 3. Creates between 6 to 12 messages per string.

MIDI_Max_E = 49
MIDI_Max_D = 58
MIDI_Max_B = 68

MIDI_Min_E = 40
MIDI_Min_D = 50
MIDI_Min_B = 59

# MIDI Ranges in C major
midi_notes_e_range = [40, 41, 43, 45, 47, 48]
midi_notes_d_range = [50, 52, 53, 55, 57]
midi_notes_b_range = [59, 60, 62, 64, 65, 67]

def generateNotes(min_midi, max_midi, n):
    # min_midi: minimum Midi value
    # max_midi: maximum Midi value
    # n: number of notes

    rng = np.random.default_rng()
    notes = rng.integers(low=min_midi, high=max_midi, size=n)
    # print(notes)

    return notes

def generateStringSpeeds(n):
    # n: number of durations
    rng = np.random.default_rng()
    durations = rng.integers(low=1, high=5, size=n)

    return durations

def generateMessages(notes, durations, n):
    # pluck_message = [[note (midi value), duration, speed, slide_toggle, timestamp]]
    messages = []
    rng = np.random.default_rng()
    speeds = rng.integers(low=1, high=10, size=n)
    curr_timestamp = 0
    for x in range(n):
        message = [notes[x], durations[x], speeds[x], 0, curr_timestamp]
        curr_timestamp+=durations[x]
        print(message)

        messages.append(message)

    return messages

def generateSong():
    print("Generating song")
    # Generate E Notes

    print("E NOTES")
    rng = np.random.default_rng()
    r_messages_E = rng.integers(low=3, high=7, size=1)
    E_notes = generateNotes(MIDI_Min_E, MIDI_Max_E, r_messages_E[0])
    E_durations = generateStringSpeeds(r_messages_E[0])
    E_messages = generateMessages(E_notes, E_durations, r_messages_E[0])
    # Generate D Notes

    print("D NOTES")
    rng = np.random.default_rng()
    r_messages_D = rng.integers(low=3, high=7, size=1)
    D_notes = generateNotes(MIDI_Min_D, MIDI_Max_D, r_messages_D[0])
    D_durations = generateStringSpeeds(r_messages_D[0])
    D_Notes = generateMessages(D_notes, D_durations, r_messages_D[0])
    # Generate B Notes

    print("B NOTES")
    rng = np.random.default_rng()
    r_messages_B = rng.integers(low=3, high=7, size=1)
    B_notes = generateNotes(MIDI_Min_B, MIDI_Max_B, r_messages_B[0])
    B_durations = generateStringSpeeds(r_messages_B[0])
    B_Notes = generateMessages(B_notes, B_durations, r_messages_B[0])


    song = [E_messages, D_notes, B_notes]

    return song

generateSong()