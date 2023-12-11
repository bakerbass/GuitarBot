from pedalboard import load_plugin
from pedalboard.io import AudioFile
from mido import Message
from pydub import AudioSegment
from pydub.playback import play

PLUGIN_PATH = '/Library/Audio/Plug-Ins/VST3/'
PLUGIN_FILE_NAME = 'AGM.VST3'

class Previewer:
    def __init__(self):
        self.plugin = load_plugin(path_to_plugin_file=PLUGIN_PATH + PLUGIN_FILE_NAME, parameter_values={'play_mode': 1,
                                                                                                        's_strum_toggle': True})
        assert self.plugin.is_instrument # will throw error if is_instrument == false
        print(PLUGIN_FILE_NAME + ' plugin loaded', flush=True)
        
        print('parameters: ')
        print(self.plugin.parameters.keys())
        
    def show_plugin_editor(self):
        self.plugin.show_editor()

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