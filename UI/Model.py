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

        self.sections = {} # Key-value pairs of form {id, Section}

    # Called by Controller, adds a new section to the Model
    def add_section(self, section_id, name):
        new_section = Section(section_id, name) # left_arm, right_arm will be initialized to empty lists
        self.sections[section_id] = new_section

    # Called by Controller, updates the data for a particular section (indexed by id)
    # Data includes name and left_arm, right_arm lists
    def update_section_data(self, section_id, left_arm, right_arm, name=None):
        section = self.sections[section_id]
        if name is not None:
            section.name = name
        section.left_arm = left_arm
        section.right_arm = right_arm

    # Called by Controller, removes a particular section (indexed by id)
    def remove_section(self, section_id):
        self.sections.pop(section_id)