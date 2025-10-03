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
    r_messages_E = rng.integers(low=30, high=35, size=1)
    E_notes = generateNotes(midi_notes_e_range, r_messages_E[0])
    E_durations = generateStringSpeeds(r_messages_E[0])
    E_messages = generateMessages(E_notes, E_durations, r_messages_E[0])
    # Generate D Notes

    print("D NOTES")
    rng = np.random.default_rng()
    r_messages_D = rng.integers(low=30, high=35, size=1)
    D_notes = generateNotes(midi_notes_d_range, r_messages_D[0])
    D_durations = generateStringSpeeds(r_messages_D[0])
    D_messages = generateMessages(D_notes, D_durations, r_messages_D[0])
    # Generate B Notes

    print("B NOTES")
    rng = np.random.default_rng()
    r_messages_B = rng.integers(low=30, high=35, size=1)
    B_notes = generateNotes(midi_notes_b_range, r_messages_B[0])
    B_durations = generateStringSpeeds(r_messages_B[0])
    B_messages = generateMessages(B_notes, B_durations, r_messages_B[0])

    all_messages = E_messages + D_messages + B_messages
    print("Combined Messages:", all_messages)

    return all_messages


#-----------
# Triad based Approach
#-----------


import random

# Voicings in the key of C
c_major_triads = [
    [40, 55, 60],  # Voicing: [E, G, C]
    [43, 52, 60],  # Voicing: [G, E, C]
    [48, 52, 67],  # Voicing: [C, E, G]
    [48, 55, 64]   # Voicing: [C, G, E]
]

d_minor_triads = [
    [41, 57, 62],  # Voicing: [F, A, D]
    [45, 50, 65]   # Voicing: [A, D, F]
]

e_minor_triads = [
    [40, 55, 59],  # Voicing: [E, G, B]
    [43, 52, 59],  # Voicing: [G, E, B]
    [47, 52, 67]   # Voicing: [B, E, G]
]

f_major_triads = [
    [41, 57, 60],  # Voicing: [F, A, C]
    [45, 53, 60],  # Voicing: [A, F, C]
    [48, 53, 65]   # Voicing: [C, F, A]
]

g_major_triads = [
    [43, 50, 59],  # Voicing: [G, D, B]
    [47, 55, 62]   # Voicing: [B, G, D]
]

a_minor_triads = [
    [40, 57, 60],  # Voicing: [E, A, C]
    [45, 52, 60],  # Voicing: [A, E, C]
    [48, 52, 64]   # Voicing: [C, E, E]
]

b_diminished_triads = [
    [41, 50, 59],  # Voicing: [F, D, B]
    [47, 50, 65]   # Voicing: [B, D, F]
]

def generate_scale_progression(iterations):
    """
    Generates a pluck message list that plays through the C Major scale.
    For each chord in the scale, a random triad voicing is chosen.

    Args:
        iterations (int): The number of times to play the full scale progression.

    Returns:
        list: A list of pluck messages formatted for the robot.
    """
    # Create a list of the chords in the key of C, in order.
    # Each element is a list of available voicings for that chord.
    chords_in_key = [
        c_major_triads,
        d_minor_triads,
        e_minor_triads,
        f_major_triads,
        g_major_triads,
        a_minor_triads,
        b_diminished_triads
    ]

    message = []
    curr_ts = 0

    # The main loop for repeating the entire scale progression
    for i in range(iterations):
        # Loop that progresses through the chords of the scale
        for chord_voicings in chords_in_key:
            # Randomly select one triad voicing from the current chord's options
            random_triad = random.choice(chord_voicings)

            # Create the pluck messages for the 3 notes in the chosen triad.
            for note in random_triad:
                # pluck_message = [[note, duration, speed, slide_toggle, timestamp]]
                rand_speed = random.randint(1, 10)
                curr_message = [note, .4, 1, 0, curr_ts]
                message.append(curr_message)

                # Increment the timestamp for the next chord in the progression.
                curr_ts += .5

    print("Scale Progression Message:", message)
    return message

def sequential_Plucks(iterations):
# Triad: Triad Voicing
    message = []
    curr_ts = 0
    triad = c_major_triads
    for x in range(iterations):
        for voice in triad:
            for note in voice:
                curr_message = [note, .1, 1, 0, curr_ts]
                message.append(curr_message)
                curr_ts += .5
    print(message)
    return message


# Example usages
# generateSong() # Random plucks in C Major
pluck_message = generate_scale_progression(12) # Play the C Major scale x times
#pluck_message = sequential_Plucks(1)