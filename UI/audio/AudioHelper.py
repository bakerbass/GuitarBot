# requires pip packages pydub, simpleaudio to be installed
# requires ffmpeg (see pydub documentation for installation instructions) 
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup

FORMAT = "m4a"

class AudioHelper: 
    @staticmethod
    def convert_m4a_to_wav():
        # convert all files in chord_recordings/m4a folder to .wav format and save as new copy to chord_recordings/wav folder
        print()

    @staticmethod
    def preview_input():
        sound = AudioSegment.from_file("UI/audio/chord_recordings/m4a/C_down.m4a", format=FORMAT)
        print('playing sample sound')
        play(sound)