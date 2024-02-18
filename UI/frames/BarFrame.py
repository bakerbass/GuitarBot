import customtkinter as ctk

BEATS_PER_BAR = 4 # should interface with the controller to get this info from combo box?
SUBDIVISIONS_PER_BEAT = 2

STRUM_BOX_WIDTH = 30
CHORD_BOX_WIDTH = STRUM_BOX_WIDTH * SUBDIVISIONS_PER_BEAT

class BarFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.addChordBoxes()
        self.addStrumBoxes()

    def addChordBoxes(self):
        for i in range(0, BEATS_PER_BAR):
            chordBoxForBeat = ctk.CTkTextbox(self, height=20, width=CHORD_BOX_WIDTH)
            chordBoxForBeat.grid(row=0, column=i*SUBDIVISIONS_PER_BEAT)

    def addStrumBoxes(self):
        for i in range(0, BEATS_PER_BAR * SUBDIVISIONS_PER_BEAT):
            strumBoxForSubdiv = ctk.CTkTextbox(self, height=20, width=STRUM_BOX_WIDTH)
            strumBoxForSubdiv.grid(row=1, column=i)