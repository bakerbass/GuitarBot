from pedalboard import load_plugin
from pedalboard.io import AudioFile
from mido import Message
from pydub import AudioSegment
from pydub.playback import play

class Previewer:
    def __init__(self):
        self.plugin = load_plugin('/Library/Audio/Plug-Ins/VST3/MONSTER Guitar v2.2022.09.vst3')
        assert self.plugin.is_instrument # will throw error if is_instrument == false
        print('Monster Guitar plugin loaded', flush=True)
        
        # set plugin mode to chords (acoustic)
        self.plugin.program = '02 [Chord] POPCORN TIME'
        print('parameters: /n' + self.plugin.parameters.keys())
        # print(self.plugin.parameters.get('program'))
        
    def show_plugin_editor(self):
        self.plugin.show_editor()

    def play_chord(self):
        sample_rate = 44100
        num_channels = 2
        with AudioFile("UI/preview/pedalboard/output-audio.wav", "w", sample_rate, num_channels) as f:
            f.write(self.plugin(
                [Message("note_on", note=80), Message("note_off", note=80, time=4)],
                sample_rate=sample_rate,
                duration=2,
                num_channels=num_channels
            ))

        # playback audio
        audio_from_file = AudioSegment.from_file("UI/preview/pedalboard/output-audio.wav")
        play(audio_from_file)