# Generates Random Notes in C for GuitarBot to play

import numpy as np
import random
# 1. Set string min and max midi values
# 2. Random amount of note changes per string (3 to 6) Random amount of string speeds per string (3 to 6)
# 3. Creates between 6 to 12 messages per string.

# MIDI Ranges in C major
midi_notes_e_range = [40, 41, 43, 45, 47, 48]
midi_notes_d_range = [50, 52, 53, 55, 57]
midi_notes_b_range = [59, 60, 62, 64, 65, 67]

def generateNotes(note_range, n):
    # min_midi: minimum Midi value
    # max_midi: maximum Midi value
    # n: number of notes
    notes  = []

    for x in range(n):
        r_note = random.choice(note_range)
        notes.append(r_note)
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
        # Convert all NumPy types to standard Python int()
        message = [int(notes[x]), int(durations[x]), int(speeds[x]), 0, int(curr_timestamp)]
        curr_timestamp += durations[x]
        print(message)

        messages.append(message)

    return messages

def generateSong():
    print("Generating song")
    # Generate E Notes

    print("E NOTES")
    rng = np.random.default_rng()
    r_messages_E = rng.integers(low=3, high=7, size=1)
    E_notes = generateNotes(midi_notes_e_range, r_messages_E[0])
    E_durations = generateStringSpeeds(r_messages_E[0])
    E_messages = generateMessages(E_notes, E_durations, r_messages_E[0])
    # Generate D Notes

    print("D NOTES")
    rng = np.random.default_rng()
    r_messages_D = rng.integers(low=3, high=7, size=1)
    D_notes = generateNotes(midi_notes_d_range, r_messages_D[0])
    D_durations = generateStringSpeeds(r_messages_D[0])
    D_messages = generateMessages(D_notes, D_durations, r_messages_D[0])
    # Generate B Notes

    print("B NOTES")
    rng = np.random.default_rng()
    r_messages_B = rng.integers(low=3, high=7, size=1)
    B_notes = generateNotes(midi_notes_b_range, r_messages_B[0])
    B_durations = generateStringSpeeds(r_messages_B[0])
    B_messages = generateMessages(B_notes, B_durations, r_messages_B[0])

    all_messages = E_messages + D_messages + B_messages
    print("Combined Messages:", all_messages)

    return all_messages

# Example usage
# generateSong()