from constants.bot_specs import DEFAULT_BPM, MIN_BPM, MAX_BPM
from constants.time_signatures import DEFAULT_TIME_SIG
from constants.chord_modes import DEFAULT_CHORD_MODE
from models.Section import Section

# model stores all of the UI's data
# model also handles the business logic for the UI -> calls UIParse.py methods
class Model:
    def __init__(self):
        self.song_title = 'Song Title'

        # TODO: add logic to limit bpm to MIN_BPM, MAX_BPM range and update view accordingly
        self.bpm = DEFAULT_BPM

        self.time_signature = DEFAULT_TIME_SIG
        self.chord_mode = DEFAULT_CHORD_MODE

        self.sections = [] # list of Section classes

    def _initialize_test_sections():
        #TODO
        pass

    def build_arm_lists():
        # Called by Controller, updates left_arm, right_arm lists for each Section
        pass

    def send_arm_lists():
        # call parse.py, pass in left_arm, right_arm lists of each Section in self.sections
        pass
