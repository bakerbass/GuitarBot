import tkinter as tk

BEATS_PER_BAR = 4 # should interface with the controller to get this info from combo box?
SUBDIVISIONS_PER_BEAT = 2
SUBDIVISIONS_PER_BAR = BEATS_PER_BAR * SUBDIVISIONS_PER_BEAT

STRUM_BOX_WIDTH = 6
CHORD_BOX_WIDTH = STRUM_BOX_WIDTH * SUBDIVISIONS_PER_BEAT

BOX_PADDING = 1

class BarFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.add_bar_of_chords_and_strums()

    def add_bar_of_chords_and_strums(self):
        self.add_bar_of_chords()
        self.add_bar_of_strums()

    def add_bar_of_chords(self):
        chord_bar_frame = tk.Frame(self)
        for i in range(0, BEATS_PER_BAR):
            chord_box_for_beat = tk.Entry(chord_bar_frame, width=CHORD_BOX_WIDTH)
            chord_box_for_beat.grid(row=0, column=i)
        chord_bar_frame.grid(row=0,column=0)

    def add_bar_of_strums(self):
        strum_bar_frame = tk.Frame(self)
        for i in range(0, SUBDIVISIONS_PER_BAR):
            strum_box_for_subdiv = tk.Entry(strum_bar_frame, width=STRUM_BOX_WIDTH)
            strum_box_for_subdiv.grid(row=0, column=i)
        strum_bar_frame.grid(row=1,column=0)