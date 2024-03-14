import tkinter as tk
from constants.bot_specs import DEFAULT_BPM, MIN_BPM, MAX_BPM
from constants.time_signatures import DEFAULT_TIME_SIG
from constants.chord_modes import DEFAULT_CHORD_MODE

# model stores all of the UI's data
# model also handles the business logic for the UI -> calls UIParse.py methods
class Model:
    def __init__(self):
        self.song_title = 'Song Title'

        # TODO: add logic to limit bpm to MIN_BPM, MAX_BPM range and update view accordingly
        self.bpm = DEFAULT_BPM
        
        self.time_signature = DEFAULT_TIME_SIG
        self.chord_mode = DEFAULT_CHORD_MODE
