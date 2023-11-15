from pedalboard import load_plugin
from pedalboard.io import AudioFile
from mido import Message

class Previewer:
    def __init__(self):
        self.plugin = load_plugin('/Library/Audio/Plug-Ins/VST3/MONSTER Guitar v2.2022.09.vst3')
        assert self.plugin.is_instrument # will throw error if is_instrument == false

        # set plugin mode to chords (acoustic)
        self.plugin.program = '02 [Chord] POPCORN TIME'
        # print(self.plugin.parameters.get('program'))
        
    def show_plugin_editor(self):
        self.plugin.show_editor()

    def play_chord(self):
        pass    