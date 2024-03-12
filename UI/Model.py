import tkinter as tk
from constants.bot_specs import DEFAULT_BPM, MIN_BPM, MAX_BPM

# model stores all of the UI's data
# model also handles the business logic for the UI -> calls UIParse.py methods
class Model:
    def __init__(self):
        # TODO: add logic to limit bpm to MIN_BPM, MAX_BPM range and update view accordingly
        self.bpm = DEFAULT_BPM
