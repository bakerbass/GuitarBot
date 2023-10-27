# requires pip packages pydub, simpleaudio to be installed
# requires ffmpeg (see pydub documentation for installation instructions) 
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup
from pydub.effects import normalize

# m4a: "m4a"
# wav: "wav"
FORMAT = "wav"

class AudioHelper: 
    @staticmethod
    def convert_m4a_to_wav():
        # convert all files in chord_recordings/m4a folder to .wav format and save as new copy to chord_recordings/wav folder
        print()

    @staticmethod
    def preview_song(left_arm, right_arm, bpm, subdivisions_per_beat):
        # print(left_arm)
        # print(right_arm)

        song = AudioSegment.silent(100) # must be at least 100 ms for built-in crossfade
        beat_duration = 60/bpm * 1000 # this accounts for tempo adjustment (default is 60 bpm)
        subdivision_duration = beat_duration/subdivisions_per_beat

        i = 0
        for bar in right_arm:
            j = 0
            last_chord = ''
            while j < len(bar):
                strum_input = bar[j]
                strum_type = strum_input.lower()

                if strum_type == 'd' or strum_type == 'u':
                    new_segment, last_chord, empty_strums = get_next_chord(i, j, left_arm, right_arm, subdivision_duration, subdivisions_per_beat, strum_type, last_chord)
                    j += empty_strums # skip over empty strum inputs that were just counted
                    song = song.append(new_segment)
                else:
                    # silence
                    song = song.append(AudioSegment.silent(duration=subdivision_duration))
                    # print('silence duration:' + subdivision_duration)
                j += 1
            i += 1

        # for this speedup implementation, set beat_duration = 1000
        # if (bpm > 60):
        #     song = speedup(song, bpm/60)
        play(song)

### helper methods below ###

def count_empty_strums(bar, start_index):
    empty_strums = 0
    for k in range(start_index, start_index + len(bar)):
        if (k < len(bar)) and bar[k] == '':
            empty_strums += 1
        else:
            break

    return empty_strums

def flat_to_sharp(chord_input):
    chord_letter = chr(ord(chord_input[0]) - 1) # previous note in scale

    if chord_input[0] == 'F' or chord_input[0] == 'C':
        # omit sharp
        chord_input = chord_letter + ('' if len(chord_input) < 3 else chord_input[2:])
    else:
        chord_input = chord_letter + '#' + ('' if len(chord_input) < 3 else chord_input[2:])
    
    # check for wraparound edge case
    if chord_letter == '@':
        chord_input = 'G' + chord_input[1:]

    return chord_input

def get_next_chord(i, j, left_arm, right_arm, subdivision_duration, subdivisions_per_beat, strum_type, last_chord):
    chord_input = left_arm[i][int(j / subdivisions_per_beat)]

    # TODO: handle invalid chord inputs
    if (chord_input == ''):
        chord_input = last_chord
    else:
        last_chord = chord_input
    
    if len(chord_input) >= 2 and chord_input[1] == 'b':
        chord_input = flat_to_sharp(chord_input)

    new_segment = AudioSegment.from_file("UI/audio/chord_recordings/" + FORMAT + "/" + chord_input + "_" + strum_type + "." + FORMAT, format=FORMAT)
    new_segment = new_segment.set_sample_width(2) # IMPORTANT (without this, >16-bit audio files will be insanely loud and distorted)
    new_segment = normalize(new_segment) # normalize amplitude

    empty_strums = count_empty_strums(right_arm[i], j + 1)
    # print(empty_strums)
    new_segment = new_segment[:subdivision_duration * (empty_strums + 1)]
    # j += empty_strums # skip over empty strum inputs that were just counted
    # print(len(new_segment))

    return new_segment, last_chord, empty_strums