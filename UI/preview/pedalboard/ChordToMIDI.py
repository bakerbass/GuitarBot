from mido import Message

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

# Takes in a chord, parses it, and returns appropriate MIDI.
### chord: list of ints in tab notation
### eightNotes: number of eigth notes chord rings
### tempo: BPM it is played in
def chord_tab_to_MIDI(chord, eightNotes, tempo):
    # TODO: use same parse logic used upon the .json to mirror same voicing bot would use

    MIDI_chord = []
    duration = eightNotes * 30/tempo
    open_note = 40 # E2 in standard tuning
    chord_idx = 0

    # TODO: make velocity correspond to duration?
    for note in chord: # assumed 6th string comes first
        MIDI_chord.insert(chord_idx, Message("note_off", note=open_note+note, time=duration, channel=0))
        MIDI_chord.insert(chord_idx, Message("note_on", note=open_note+note, velocity=80, channel=0))
        chord_idx += 1
        open_note += 6 # perfect-fourth, next string

    return MIDI_chord