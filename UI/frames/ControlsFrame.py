import tkinter as tk

class ControlsFrame(tk.Frame):
    def __init__(self, master, width, height):
        super().__init__(master, width=width, height=height)

        # Chord Mode
        chord_mode_label = tk.Label(self, text="Chord Mode")
        chord_mode_label.grid(row=0, column=0) 

        # Chord Notations
        notation_label = tk.Label(self, text="Chord Notations")
        notation_label.grid(row=1, column=0)

        # Song Title
        song_title_label = tk.Label(self, text="Song Title")
        song_title_label.grid(row=0, column=2)

        # Save, Load, Send to Bot
        save_button = tk.Button(self, text="Save")
        save_button.grid(row=1, column=1)

        load_button = tk.Button(self, text="Load")
        load_button.grid(row=1, column=2)

        send_to_bot_button = tk.Button(self, text="Send to Bot")
        send_to_bot_button.grid(row=1, column=3)

        # BPM
        bpm_label = tk.Label(self, text="BPM")
        bpm_label.grid(row=0, column=5)

        # Time signature
        time_signature = tk.Label(self, text="Time signature")
        time_signature.grid(row=1, column=5)


