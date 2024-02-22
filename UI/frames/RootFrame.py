import tkinter as tk
from frames.SongFrame import SongFrame

class RootFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        # add widgets onto the frame...
        self.label = tk.Label(self, text='The quick brown fox jumped over the lazy dog.')
        self.label.grid(row=0, column=0, padx=20)

        self.song_frame = SongFrame(master=self)

        self.sections = SongFrame(master=self, width=self.winfo_screenwidth(), height=self.winfo_screenheight() * 0.7)
        self.sections.grid(row=1)
