# requires pip packages pydub, simpleaudio to be installed
# requires ffmpeg (see pydub documentation for installation instructions) 
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup

# m4a: "m4a"
# wav: "wav"
FORMAT = "m4a"

class AudioHelper: 
    @staticmethod
    def convert_m4a_to_wav():
        # convert all files in chord_recordings/m4a folder to .wav format and save as new copy to chord_recordings/wav folder
        print()

    # NOTE: implementation is synced to 60 bpm.
    @staticmethod
    def preview_song(left_arm, right_arm, bpm, subdivisions_per_beat):
        print(left_arm)
        print(right_arm)

        song = AudioSegment.silent(100) # must be at least 100 ms for built-in crossfade
        beat_duration = 60/bpm * 1000 # this accounts for tempo adjustment

        i = 0
        for bar in right_arm:
            j = 0
            last_chord = ''
            for strum_input in bar:
                if (strum_input.lower() == 'd'):
                    # down-strum
                    chord_input = left_arm[i][int(j / subdivisions_per_beat)]

                    # TODO: handle invalid chord inputs
                    if (chord_input == ''):
                        chord_input = last_chord
                    else:
                        last_chord = chord_input

                    new_segment = AudioSegment.from_file("UI/audio/chord_recordings/" + FORMAT + "/" + chord_input + "_d." + FORMAT, format=FORMAT)
                    
                    if (j + 1 < len(right_arm[i]) and right_arm[i][j + 1] == ''):
                        # let chord ring for full beat
                        new_segment = new_segment[:beat_duration]
                    else:
                        new_segment = new_segment[:beat_duration/subdivisions_per_beat]

                    song = song.append(new_segment)
                elif (strum_input.lower() == 'u'):
                    #up-strum
                    chord_input = left_arm[i][int(j / subdivisions_per_beat)]
                    print(chord_input)

                    # TODO: handle invalid chord inputs
                    if (chord_input == ''):
                        chord_input = last_chord
                    else:
                        last_chord = chord_input

                    new_segment = AudioSegment.from_file("UI/audio/chord_recordings/" + FORMAT + "/" + chord_input + "_u." + FORMAT, format=FORMAT)
                    
                    if (j + 1 < len(right_arm[i]) and right_arm[i][j + 1] == ''):
                        # let chord ring for full beat
                        new_segment = new_segment[:beat_duration]
                    else:
                        new_segment = new_segment[:beat_duration/subdivisions_per_beat]

                    song = song.append(new_segment)
                else:
                    # silence
                    song = song.append(AudioSegment.silent(duration=beat_duration/subdivisions_per_beat))
                j += 1
            i += 1

        # for this speedup implementation, set beat_duration = 1000
        # if (bpm > 60):
        #     song = speedup(song, bpm/60)
        play(song)