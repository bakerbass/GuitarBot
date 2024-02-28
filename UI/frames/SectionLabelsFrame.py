import tkinter as tk
import tkinter.ttk as ttk
from constants.strum_patterns import strum_options

class SectionLabelsFrame(tk.Frame):
    def __init__(self, master, width, height):
        super().__init__(master=master, width=width, height=height)

        self.height = height
        self.width = width
        self.name = tk.StringVar(self, "Name")
        self.strum_pattern = tk.StringVar(self)

        # configure rows
        for i in range(2):
            self.grid_rowconfigure(i, minsize=self.height * 0.25)

        # configure columns
        for i in range(4):
            self.grid_columnconfigure(i, minsize=self.width * 0.2)

        # name entry box
        name_entry = ttk.Entry(self, textvariable=self.name, justify='center', width=6)
        name_entry.grid(row=0, column=0, columnspan=2)

        # clear, delete icons
        # TODO

        # chords label
        chords_lbl = tk.Label(self, text='Chords:')
        chords_lbl.grid(row=0, column=2, columnspan=2, sticky='EW')
            
        # strum options dropdown
        strum_options_dd = ttk.OptionMenu(self, self.strum_pattern, 'Strum Pattern', *strum_options)
        strum_options_dd.grid(row=1, column=2, columnspan=2)

