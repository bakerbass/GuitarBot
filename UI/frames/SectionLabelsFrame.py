import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
from constants.strum_patterns import strum_options
from PIL import Image, ImageTk

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
        img = Image.open('UI/icons/trash-16px.png')
        self.trash_icon = ImageTk.PhotoImage(img)
        trash_btn = ctk.CTkButton(self, image=self.trash_icon, width=0, border_width=0, border_spacing=0, text='', fg_color='transparent')
        trash_btn.grid(row=1, column=0)

        img = Image.open('UI/icons/eraser-16px.png')
        self.eraser_icon = ImageTk.PhotoImage(img)
        eraser_btn = ctk.CTkButton(self, image=self.eraser_icon, width=0, border_width=0, border_spacing=0, text='', fg_color='transparent')
        eraser_btn.grid(row=1, column=1)

        # chords label
        chords_lbl = tk.Label(self, text='Chords:')
        chords_lbl.grid(row=0, column=2, columnspan=2, sticky='EW')
            
        # strum options dropdown
        strum_options_dd = ttk.OptionMenu(self, self.strum_pattern, 'Strum Pattern', *strum_options)
        strum_options_dd.grid(row=1, column=2, columnspan=2)

