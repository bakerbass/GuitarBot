from pedalboard import load_plugin
from pedalboard.io import AudioFile
from mido import Message
from pydub import AudioSegment
from pydub.playback import play

VST3_PATH = '/Library/Audio/Plug-Ins/VST3/'
AU_PATH = '/Library/Audio/Plug-Ins/Components/'
# PLUGIN_FILE_NAME = 'AGML2.component'
PLUGIN_FILE_NAME = 'DSK Dynamic Guitars.component'

class Previewer:
    def __init__(self):
        self.plugin = load_plugin(path_to_plugin_file=AU_PATH + PLUGIN_FILE_NAME)
        assert self.plugin.is_instrument # will throw error if is_instrument == false
        print(PLUGIN_FILE_NAME + ' plugin loaded', flush=True)
        
        # # set plugin mode to chords (acoustic)
        # self.plugin.program = '02 [Chord] POPCORN TIME'
        print('parameters: ')
        print(self.plugin.parameters.keys())
        # print(self.plugin.parameters.get('program'))
        
    def show_plugin_editor(self):
        self.plugin.show_editor()

    # Monster Guitar Plug-In Specifications:
    # NOTE: Turn sustain pedal all the way up
    #
    # To control PITCH: C2-B2
    #
    # To control CHORD (adjust for strum range): 
    #   5th (power) = C3
    #   Minor = C#3
    #   Sus2 = D3
    #   Min6 = D#3
    #   Major = E3
    #   Sus4 = F3
    #   Dim = F#3
    #   Dom7 = G3
    #   Aug = G#3
    #   Maj6 = A3
    #   Min7 = A#3
    #   Maj7 = B3
    #   
    # To control STRUM: 
    #   Normal = C3-B3 range
    #   Short (muted) = C4 - B4 range
    #   Long = C5-B5 range
    #   
    # midi int encodings: https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
    # mido message specifications: https://mido.readthedocs.io/en/stable/message_types.html 
    #
    # NOTE: Send two midi notes at a time to play chord/strum together
    #
    def play_chord(self):
        sample_rate = 44100
        num_channels = 2
        with AudioFile("UI/preview/pedalboard/output-audio.wav", "w", sample_rate, num_channels) as f:
            f.write(self.plugin(
                # Pitch = C (36), Strum = Normal, Major (52)
                # [Message("note_on", note=52, velocity=80, channel=0), 
                #  Message("note_off", note=52, time=4, channel=0), # duration 4 seconds
                #  Message("note_on", note=36, velocity=80, channel=1), 
                #  Message("note_off", note=36, time=4, channel=1)], # duration 4 seconds
                # sample_rate=sample_rate,
                # duration=4,
                # num_channels=num_channels
                [Message("note_on", note=60), Message("note_on", note=80),
                Message("note_off", note=60, time=2), Message("note_off", note=80, time=2)],
                duration=2, # seconds
                sample_rate=sample_rate,
            ))

        # playback audio
        audio_from_file = AudioSegment.from_file("UI/preview/pedalboard/output-audio.wav")
        play(audio_from_file)