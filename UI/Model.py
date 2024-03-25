from constants.bot_specs import DEFAULT_BPM, MIN_BPM, MAX_BPM
from constants.time_signatures import DEFAULT_TIME_SIG
from constants.chord_modes import DEFAULT_CHORD_MODE
from parse import parseleft_M, parseright_M
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
        # David: I assumed a section was a tuple formatted [left_arm, right_arm]

    # Called by Controller, adds a new section to the Model
    def add_section(self, id, name):
        new_section = Section(id, name) # left_arm, right_arm will be initialized to empty lists
        self.sections[id] = new_section

    # Called by Controller, updates the data for a particular section (indexed by id)
    # Data includes name and left_arm, right_arm lists
    def update_section_data(self, id, name, left_arm, right_arm):
        section = self.sections[id]
        section.name = name
        section.left_arm = left_arm
        section.right_arm = right_arm

    # Called by Controller, clears all left_arm and right_arm data for a particular section (indexed by id)
    def clear_section_data(self, id):
        self.sections[id].clear()

    # Called by Controller, removes a particular section (indexed by id)
    def remove_section(self, id):
        self.sections.pop(id)

    def send_arm_lists(self):
        # TODO (David)
        # call parse.py, pass in left_arm, right_arm lists of each Section in self.sections
        # modify parse.py to accept new chord notations

        for section in self.sections.values():
            print(section.left_arm, section.right_arm)
            parseleft_M(section.left_arm, 8) # i was unsure what measure time was, i hardcoded to assumption it's number of beat subdivisions in a measure for 4/4
            parseright_M(section.right_arm, 8)

            # incomplete!!!
