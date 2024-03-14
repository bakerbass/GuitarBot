import tkinter as tk
import tkinter.ttk as ttk
from constants.strum_patterns import strum_options

# TODO: fix icons, currently showing up as white boxes
global trash_icon, eraser_icon # necessary so that tkinter doesn't garbage collect the images after the init method

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

        # trash, eraser icon buttons
        trash_icon = tk.PhotoImage(file='UI/icons/trash-16px.png')
        trash_btn = tk.Button(self, image=trash_icon, borderwidth=0)
        trash_btn.grid(row=1, column=0)

        eraser_icon = tk.PhotoImage(file='UI/icons/eraser-16px.png')
        eraser_btn = tk.Button(self, image=eraser_icon, borderwidth=0)
        eraser_btn.grid(row=1, column=1)

        # chords label
        chords_lbl = tk.Label(self, text='Chords:')
        chords_lbl.grid(row=0, column=2, columnspan=2, sticky='EW')
            
        # strum options dropdown
        strum_options_dd = ttk.OptionMenu(self, self.strum_pattern, 'Strum Pattern', *strum_options)
        strum_options_dd.grid(row=1, column=2, columnspan=2)

