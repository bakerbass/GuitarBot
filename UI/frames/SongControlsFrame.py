import tkinter as tk
import tkinter.ttk as ttk
from constants.time_signatures import time_signature_options
from constants.chord_modes import chord_mode_options
from constants.bot_specs import MIN_BPM, MAX_BPM

class SongControlsFrame(tk.Frame):
    def __init__(self, master, width, height):
        super().__init__(master, width=width, height=height)
        self.width = width
        self.height = height
        self.title = tk.StringVar(self, 'Song Title')
        self.time_signature = tk.StringVar(self)
        self.bpm = tk.IntVar(self, 60)
        self.chord_mode = tk.StringVar(self)

        # configure row height
        for i in range(2):
            self.grid_rowconfigure(i, minsize=self.height * 0.25)

        # configure column width
        for i in range(10):
            if i in range(3, 6):
                # make middle columns tighter
                self.grid_columnconfigure(i, minsize=self.width * 0.05, pad=0)
            elif i in range(8, 10):
                self.grid_columnconfigure(i, minsize=self.width * 0.06, pad=0)
            else:
                self.grid_columnconfigure(i, minsize=self.width * 0.135, pad=0)

        # Chord Mode dropdown
        chord_mode_dd = ttk.OptionMenu(self, self.chord_mode, 'Chord Mode', *chord_mode_options)
        chord_mode_dd.grid(row=0, column=0, sticky='W') 

        # Chord Notations btn
        chord_notation_btn = tk.Button(self, text="Chord Notations")
        chord_notation_btn.grid(row=1, column=0, sticky='W')

        # Song Title
        song_title_lbl = tk.Label(self, textvariable=self.title, font=('TkDefaultFont', 16, 'bold'))
        song_title_lbl.grid(row=0, column=4)

        # Save, Load, Send btns
        save_btn = tk.Button(self, text="Save")
        save_btn.grid(row=1, column=3, sticky='E')

        load_btn = tk.Button(self, text="Load")
        load_btn.grid(row=1, column=4)

        send_btn = tk.Button(self, text="Send")
        send_btn.grid(row=1, column=5, sticky='W')

        # BPM label and text entry
        bpm_label = tk.Label(self, text="BPM:")
        bpm_label.grid(row=0, column=8, sticky='E')

        bpm_entry = ttk.Spinbox(self, textvariable=self.bpm, from_=MIN_BPM, to=MAX_BPM, width=3, justify='left')
        bpm_entry.grid(row=0, column=9, sticky='EW')

        # Time signature label and dropdown
        time_sig_lbl = tk.Label(self, text="Time Signature:")
        time_sig_lbl.grid(row=1, column=8, sticky='E')

        time_sig_dd = ttk.OptionMenu(self, self.time_signature, "4/4", *time_signature_options)
        time_sig_dd.grid(row=1, column=9, sticky='EW')