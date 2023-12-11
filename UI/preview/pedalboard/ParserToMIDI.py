from mido import Message

MAJOR_THIRD, PERFECT_FOURTH = 4, 5
curr_chord_name = ""

# Given a position, seeks to the next strum
def get_next_chord_strum(left_arm, right_arm, tempo, measure_idx, subdiv_idx):
    next_chord_name = curr_chord_name # holds next chord if change made in meantime

    subdiv_idx += 1
    curr_chord_subdiv_count = 1
    
    while measure_idx < len(right_arm):
        while subdiv_idx < len(right_arm[measure_idx]):
            if left_arm[measure_idx][subdiv_idx] != "":
                next_chord_name = left_arm[measure_idx][subdiv_idx]
            if right_arm[measure_idx][subdiv_idx] != "":
                break # strum performed
            curr_chord_subdiv_count += 1
            subdiv_idx += 1
        subdiv_idx = 0
        measure_idx += 1

    MIDI_note_ons, MIDI_note_offs = chord_name_to_MIDI(curr_chord_name, curr_chord_subdiv_count, right_arm[measure_idx][subdiv_idx].lower() == "d")
    MIDI_tuple = (MIDI_note_ons, MIDI_note_offs, tempo/120 * curr_chord_subdiv_count) # assumes eight notes the subdiv
    curr_chord_name = next_chord_name

    return measure_idx, subdiv_idx, MIDI_tuple

# Takes in arms and timing info information, uses them to create MIDI message for whole song
# left_arm: same ideas as one in UIGen.py
# right_arm: created in UIGen.py
def arms_to_MIDI(left_arm, right_arm, tempo):
    MIDI_song = [] # list of tuples of form (note_ons, note_offs, duration in seconds for chord)

    curr_chord_name = ""
    measure_idx, subdiv_idx = 0, 0

    # Assumes a chord will be specified in the first slot...
    while measure_idx < len(left_arm):
        measure_idx, subdiv_idx, MIDI_tuple = get_next_chord_strum(left_arm, right_arm, tempo, measure_idx, subdiv_idx)
        MIDI_song.append(MIDI_tuple)

    return MIDI_song

# Takes in tab and timing information, mapping inputs to MIDI.
###        chord: name of chord
### subdivisions: number of eigth notes chord rings
### is_downstrum: true if downstrum, false if upstrum
def chord_name_to_MIDI(chord_name, subdivisions, is_downstrum):
    MIDI_note_ons, MIDI_note_offs = [], []
    open_note = 40 # E2 in standard tuning
    chord_tab = chords[chord_name] # list of ints in tab notation where 6th string, low bass, comes first

    string_idx = 6
    # TODO: velocity, or loudness, should vary by note to correspond with upstrum/downstrum?
    # should emphasize 1 and 3 beats in 4/4?
    for fret_number_of_note in chord_tab:
        MIDI_note_ons.append(Message("note_on", note=open_note+fret_number_of_note, velocity=80, channel=0))
        MIDI_note_offs.append(Message("note_off", note=open_note+fret_number_of_note, channel=0)) # removed duration, doesn't work w/ VST???
        if string_idx != 3:
            open_note += PERFECT_FOURTH
        else:
            open_note += MAJOR_THIRD
        string_idx -= 1

    return MIDI_note_ons, MIDI_note_offs

# This belongs in its own file, copy-pasted here as a shortcut for now, writing this at 1:50 am lol
chords = {
    "AM": [5, 7, 7, 6, 5, 5],
    "AM7": [],
    "AM9": [],
    "Am": [5, 0, 7, 6, 5, 5],
    "Am7": ['X', 3, 1, 3, 1, 3],
    "Am9": ['X', 3, 0, 3, 4, 3],
    "ADim": ['X', 3, 1, 'X', 1, 2],
    "ADom": ['X', 0, 2, 0, 2, 0],
    "ASus2": ['X', 0, 'X', 'X', 0, 0],
    "ASus4": ['X', 0, 2, 2, 3, 3],
    "Am11": [8, 6, 5, 5, 6, 6],
    "Am7b5": ['X', 3, 1, 3, 1, 2],
    "A5": ['X', 0, 'X', 'X', 'X', 0],
    "A7": ['X', 0, 2, 0, 2, 0],
    "AM6": [5, 4, 4, 'X', 5, 5],
    "Am6": [5, 3, 2, 2, 0, 0],
    "BM": [7, 6, 4, 4, 0, 7],
    "BM7": [7, 9, 8, 8, 7, 7],
    "BM9": [],
    "Bm": [7, 9, 9, 7, 7, 7],
    "Bm7": ['X', 2, 0, 2, 0, 2],
    "Bm9": [],
    "BDim": [],
    "BDom": [7, 0, 4, 4, 4, 5],
    "BSus2": ['X', 2, 'X', 'X', 2, 2],
    "BSus4": [7, 7, 9, 9, 7, 7],
    "Bm11": [],
    "Bm7b5": ['X', 2, 0, 2, 0, 1],
    "B5": ['X', 2, 'X', 'X', 0, 2],
    "B7": ['X', 2, 1, 2, 0, 2],
    "BM6": ['X', 2, 1, 1, 0, 2],
    "Bm6": [],
    "CM": ['X', 3, 2, 0, 1, 0],
    "CM7": ['X', 3, 2, 4, 0, 3],
    "CM9": ['X', 3, 0, 3, 5, 3],
    "Cm": [8, 6, 5, 0, 8, 8],
    "Cm7": ['X', 3, 1, 3, 1, 3],
    "Cm9": ['X', 3, 0, 3, 4, 3],
    "CDim": ['X', 3, 1, 'X', 1, 2],
    "CDom": ['X', 3, 2, 3, 'X', 3],
    "CSus2": [8, 5, 5, 0, 8, 8, ],
    "CSus4": [8, 8, 5, 5, 6, 8],
    "Cm11": [8, 5, 5, 8, 6, 6],
    "Cm7b5": ['X', 3, 1, 3, 1, 2],
    "C5": ['X', 3, 'X', 0, 1, 3],
    "C7": [3, 2, 0, 0, 0, 0],
    "CM6": ['X', 3, 2, 2, 1, 3],
    "Cm6": ['X', 3, 1, 2, 3, 3],
    "DM": ['X', 'X', 0, 2, 3, 2],
    "DM7": ['X', 'X', 0, 2, 2, 2],
    "DM9": ['X', 2, 1, 'X', 2, 2],
    "Dm": ['X', 'X', 0, 2, 3, 1],
    "Dm7": ['X', 'X', 0, 2, 1, 1],
    "Dm9": ['X', 5, 7, 5, 6, 0],
    "DDim": ['X', 'X', 0, 1, 3, 1],
    "DDom": ['X', 'X', 0, 2, 1, 2],
    "DSus2": ['X', 'X', 0, 2, 'X', 0],
    "DSus4": ['X', 5, 5, 0, 3, 5],
    "Dm11": [10, 0, 10, 10, 8, 0],
    "Dm7b5": ['X', 'X', 0, 1, 1, 1],
    "D5": ['X', 'X', 0, 2, 'X', 'X'],
    "D7": ['X', 'X', 0, 2, 1, 2],
    "DM6": ['X', 5, 4, 4, 3, 5],
    "Dm6": ['X', 5, 3, 4, 5, 5],
    "EM": [0, 2, 2, 1, 0, 0],
    "EM7": [0, 'X', 1, 1, 0, 0],
    "EM9": [0, 2, 2, 1, 0, 2],
    "Em": [0, 2, 2, 0, 0, 0],
    "Em7": [0, 2, 0, 0, 3, 0],
    "Em9": [0, 2, 0, 0, 0, 2],
    "EDim": [0, 7, 8, 0, 8, 0],
    "EDom": [0, 2, 0, 1, 0, 0],
    "ESus2": ['X', 'X', 0, 2, 'X', 0],
    "ESus4": [0, 2, 2, 2, 0, 0],
    "Em11": [10, 0, 10, 10, 8, 10],
    "Em7b5": [0, 1, 0, 0, 3, 3],
    "E5": [0, 'X', 'X', 'X', 0, 0],
    "E7": [0, 'X', 0, 1, 0, 0],
    "EM6": [0, 2, 2, 4, 2, 4],
    "Em6": [0, 2, 4, 0, 2, 2],
    "FM": [1, 3, 3, 2, 1, 1],
    "FM7": [1, 0, 3, 2, 1, 0],
    "FM9": [1, 0, 1, 0, 1, 3],
    "Fm": ['X', 'X', 3, 1, 1, 4],
    "Fm7": [1, 3, 1, 1, 4, 1],
    "Fm9": [1, 3, 1, 1, 1, 3],
    "FDim": ['X', 'X', 3, 4, 6, 4],
    "FDom": [1, 3, 1, 2, 1, 1],
    "FSus2": [1, 'X', 'X', 0, 1, 1],
    "FSus4": [1, 1, 3, 3, 1, 1],
    "Fm11": [],
    "Fm7b5": [1, 2, 3, 1, 4, 1],
    "F5": [1, 'X', 'X', 'X', 1, 1],
    "F7": [1, 0, 'X', 'X', 1, 0],
    "FM6": [1, 0, 0, 2, 1, 1],
    "Fm6": [1, 3, 0, 1, 1, 3],
    "GM": [3, 2, 0, 0, 0, 3],
    "GM7": [3, 1, 0, 0, 0, 2],
    "GM9": [3, 0, 0, 2, 0, 1],
    "Gm": [3, 1, 0, 0, 3, 3],
    "Gm7": [3, 1, 0, 0, 3, 1],
    "Gm9": [3, 0, 0, 3, 3, 1],
    "GDim": [3, 1, 'X', 0, 2, 3],
    "GDom": ['X', 10, 10, 0, 8, 10, 1],
    "GSus2": [1, 'X', 'X', 0, 1, 1],
    "GSus4": [3, 5, 3, 0, 0, 3],
    "Gm11": [],
    "Gm7b5": [3, 1, 3, 3, 2, 1],
    "G5": [],
    "G7": [],
    "GM6": [3, 2, 0, 0, 3, 0],
    "Gm6": [3, 1, 0, 2, 3, 0],
    "A#M": ['X', 1, 0, 3, 3, 1],
    "A#M7": [6, 0, 3, 3, 3, 5],
    "A#M9": [],
    "A#m": ['X', 1, 3, 3, 2, 1],
    "A#m7": [6, 8, 8, 6, 9, 9],
    "A#m9": [],
    "A#Dim": [6, 4, 'X', 6, 5, 0],
    "A#Dom": [],
    "A#Sus2": [6, 3, 3, 3, 6, 6],
    "A#Sus4": [6, 6, 3, 3, 4, 6],
    "A#m11": [],
    "A#m7b5": ['X', 1, 2, 1, 2, 0],
    "A#5": ['X', 1, 3, 3, 'X', 1],
    "A#7": [6, 8, 6, 7, 6, 6],
    "A#M6": ['X', 1, 0, 0, 'X', 1],
    "A#m6": [],
    "C#M": ['X', 4, 6, 6, 6, 4],
    "C#M7": [9, 8, 6, 6, 6, 8],
    "C#M9": [9, 6, 6, 8, 6, 9],
    "C#m": ['X', 4, 6, 6, 5, 0],
    "C#m7": ['X', 4, 2, 4, 0, 4],
    "C#m9": [9, 6, 6, 6, 0, 0],
    "C#Dim": ['X', 4, 2, 0, 2, 0],
    "C#Dom": ['X', 4, 6, 4, 6, 4],
    "C#Sus2": ['X', 4, 6, 6, 4, 4],
    "C#Sus4": ['X', 4, 4, 'X', 2, 4],
    "C#m11": [9, 9, 6, 8, 6, 7],
    "C#m7b5": ['X', 4, 2, 0, 0, 0],
    "C#5": ['X', 4, 6, 6, 'X', 2],
    "C#7": ['X', 4, 6, 5, 6, 4],
    "C#M6": ['X', 4, 3, 3, 2, 4],
    "C#m6": ['X', 4, 6, 3, 4, 0],
    "D#M": ['X', 6, 5, 0, 4, 6],
    "D#M7": ['X', 6, 0, 0, 4, 6],
    "D#M9": ['X', 6, 8, 0, 6, 6],
    "D#m": ['X', 6, 4, 'X', 4, 6],
    "D#m7": ['X', 6, 4, 6, 4, 6],
    "D#m9": [],
    "D#Dim": ['X', 6, 4, 'X', 4, 5],
    "D#Dom": ['X', 6, 8, 8, 8, 9],
    "D#Sus2": ['X', 6, 8, 8, 6, 6],
    "D#Sus4": ['X', 6, 6, 'X', 4, 6],
    "D#m11": [],
    "D#m7b5": ['X', 'X', 1, 2, 2, 2],
    "D#5": ['X', 6, 8, 8, 'X', 6],
    "D#7": ['X', 6, 8, 7, 8, 6],
    "D#M6": ['X', 'X', 1, 3, 1, 3],
    "D#m6": ['X', 6, 4, 5, 6, 6],
    "F#M": [2, 4, 4, 3, 4, 4],
    "F#M7": [2, 4, 3, 3, 2, 2],
    "F#M9": [2, 1, 2, 1, 2, 0],
    "F#m": ['X', 'X', 4, 2, 2, 2],
    "F#m7": [2, 0, 4, 2, 2, 0],
    "F#m9": [2, 0, 2, 1, 2, 0],
    "F#Dim": [2, 0, 'X', 2, 1, 2],
    "F#Dom": [2, 4, 4, 3, 2, 0],
    "F#Sus2": [2, 'X', 'X', 1, 2, 2],
    "F#Sus4": [2, 4, 4, 4, 2, 2],
    "F#m11": [],
    "F#m7b5": [2, 0, 2, 2, 1, 0],
    "F#5": [2, 4, 4, 'X', 2, 2],
    "F#7": ['X', 'X', 4, 3, 2, 1],
    "F#M6": ['X', 'X', 4, 6, 4, 6],
    "F#m6": [2, 0, 1, 1, 2, 2],
    "G#M": [4, 6, 6, 5, 4, 4],
    "G#M7": [4, 6, 5, 5, 4, 4],
    "G#M9": [4, 6, 4, 5, 4, 6],
    "G#m": [4, 6, 6, 4, 4, 4],
    "G#m7": ['X', 'X', 6, 8, 7, 7],
    "G#m9": [4, 6, 4, 4, 4, 6],
    "G#Dim": [4, 2, 0, 4, 0, 4],
    "G#Dom": [4, 6, 4, 5, 4, 4],
    "G#Sus2": [4, 6, 6, 'X', 4, 6],
    "G#Sus4": [4, 6, 6, 6, 4, 4],
    "G#m11": [],
    "G#m7b5": [4, 6, 4, 4, 4, 5],
    "G#5": [4, 6, 6, 'X', 4, 4],
    "G#7": [4, 3, 1, 0, 4, 4],
    "G#M6": [4, 3, 3, 1, 4, 4],
    "G#m6": [4, 2, 3, 3, 4, 4],
    "AbM": [4, 6, 6, 5, 4, 4],
    "AbM7": [],
    "AbM9": [],
    "Abm": [4, 6, 6, 4, 4, 4],
    "Abm7": ['X', 'X', 6, 8, 7, 7],
    "Abm9": [4, 6, 4, 4, 0, 6],
    "AbDim": [4, 2, 0, 4, 0, 4],
    "AbDom": [4, 6, 4, 5, 4, 6],
    "AbSus2": [4, 1, 1, 3, 4, 4],
    "AbSus4": [4, 4, 6, 6, 4, 4],
    "Abm11": [],
    "Abm7b5": [4, 2, 0, 4, 0, 2],
    "Ab5": [4, 6, 6, 'X', 4, 4],
    "Ab7": [4, 6, 5, 5, 4, 4],
    "AbM6": [4, 6, 6, 5, 6, 4],
    "Abm6": [],
    "BbM": ['X', 1, 0, 3, 3, 1],
    "BbM7": [6, 0, 0, 'X', 6, 5],
    "BbM9": [],
    "Bbm": ['X', 1, 3, 3, 2, 1],
    "Bbm7": ['X', 1, 3, 1, 2, 1],
    "Bbm9": [],
    "BbDim": [],
    "BbDom": ['X', 1, 3, 2, 1, 1],
    "BbSus2": ['X', 1, 3, 3, 1, 1],
    "BbSus4": [6, 8, 8, 8, 6, 6],
    "Bbm11": [],
    "Bbm7b5": [6, 4, 6, 6, 5, 4],
    "Bb5": ['X', 1, 3, 3, 'X', 1],
    "Bb7": ['X', 1, 0, 1, 3, 1],
    "BbM6": ['X', 1, 0, 0, 3, 2],
    "Bbm6": [],
    "DbM": ['X', 4, 6, 6, 6, 4],
    "DbM7": ['X', 4, 6, 5, 6, 4],
    "DbM9": [9, 6, 6, 8, 6, 7],
    "Dbm": [9, 7, 'X', 9, 9, 0],
    "Dbm7": ['X', 4, 2, 4, 0, 4],
    "Dbm9": ['X', 4, 6, 4, 4, 0],
    "DbDim": ['X', 4, 2, 0, 2, 0],
    "DbDom": ['X', 4, 6, 4, 6, 6],
    "DbSus2": [9, 6, 6, 8, 9, 9],
    "DbSus4": ['X', 4, 4, 1, 2, 2],
    "Dbm11": [9, 9, 6, 8, 0, 0],
    "Dbm7b5": ['X', 4, 2, 0, 0, 3],
    "Db5": ['X', 4, 6, 6, 'X', 4],
    "Db7": ['X', 4, 3, 1, 0, 1],
    "DbM6": ['X', 4, 3, 3, 2, 4],
    "Dbm6": ['X', 4, 2, 3, 4, 4],
    "EbM": ['X', 6, 5, 0, 4, 6],
    "EbM7": ['X', 6, 0, 0, 4, 6],
    "EbM9": ['X', 6, 5, 0, 6, 6],
    "Ebm": ['X', 6, 8, 8, 7, 6],
    "Ebm7": ['X', 6, 8, 6, 7, 6],
    "Ebm9": [],
    "EbDim": ['X', 'X', 1, 2, 4, 2],
    "EbDom": ['X', 6, 5, 6, 5, 6],
    "EbSus2": ['X', 6, 8, 8, 6, 6],
    "EbSus4": ['X', 6, 6, 'X', 4, 6],
    "Ebm11": [],
    "Ebm7b5": ['X', 6, 4, 6, 4, 5],
    "Eb5": ['X', 6, 8, 8, 'X', 6],
    "Eb7": ['X', 6, 8, 6, 8, 6],
    "EbM6": ['X', 6, 5, 5, 4, 6],
    "Ebm6": ['X', 6, 4, 5, 6, 6],
}

# Each interval "constant" holds the appropriate offset
# MINOR_FIRST, FIRST, MINOR_SECOND, MINOR_THIRD, MAJOR_THIRD = 1, 2, 3, 4, 5
# PERFECT_FOURTH, PERFECT_FIFTH, MINOR_SIXTH, MAJOR_SIXTH = 6, 7, 8, 9
# MINOR_SEVENTH, MAJOR_SEVENTH, OCTAVE = 10, 11, 12
# Function that returns an E major shape MIDI voicing of the given chord formatted in a MIDO message.
### chord: chord name, 
### eightNotes: number of eigth notes chord rings
### tempo: BPM it is played in
### NOTE: Assumes chord is not an inversion, logic can be adjusted later to check for / char
# def barre_chord(chord, eightNotes, tempo):
#     rootNoteNum = ord(chord[0]) - 29 # uppercase ASCII -> MIDI bass note
#     offsetIfMinor = -1 if (len(chord) > 1 and chord[1] == 'm') else 0
#     duration = eightNotes * 30/tempo
#     if (rootNoteNum < 40): # ensures no dips below standard tuning E2 limit
#         rootNoteNum += OCTAVE
#     # TODO: adjust velocity to scale with duration?
#     return [Message("note_on", note=rootNoteNum, velocity=80, channel=0),
#             Message("note_on", note=rootNoteNum+PERFECT_FIFTH, velocity=80, channel=0),
#             Message("note_on", note=rootNoteNum+OCTAVE, velocity=80, channel=0),
#             Message("note_on", note=rootNoteNum+OCTAVE+MAJOR_THIRD+offsetIfMinor, velocity=80, channel=0),
#             Message("note_on", note=rootNoteNum+OCTAVE+PERFECT_FIFTH, velocity=80, channel=0),
#             Message("note_on", note=rootNoteNum+2*OCTAVE, velocity=80, channel=0),
#                 Message("note_off", note=rootNoteNum, time=duration, channel=0),
#                 Message("note_off", note=rootNoteNum+PERFECT_FIFTH, time=duration, channel=0),
#                 Message("note_off", note=rootNoteNum+OCTAVE, time=duration, channel=0),
#                 Message("note_off", note=rootNoteNum+OCTAVE+MAJOR_THIRD+offsetIfMinor, time=duration, channel=0),
#                 Message("note_off", note=rootNoteNum+OCTAVE+PERFECT_FIFTH, time=duration, channel=0),
#                 Message("note_off", note=rootNoteNum+2*OCTAVE, time=duration, channel=0)]
