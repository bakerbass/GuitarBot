import tkinter as tk
from tkinter.constants import *
from frames.SectionFrame import SectionFrame

class SongFrame(tk.Canvas):
    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, *args, **kwargs)

        self.vscrollbar = tk.Scrollbar(self, orient=VERTICAL)
        self.vscrollbar.pack(side=RIGHT)
        
        self.add_section() # first section

            
    def add_section(self):
        self.first_section = SectionFrame(master=self, width=int(self.winfo_screenwidth() * 0.8), height=int(self.winfo_screenwidth() * 0.8))
        self.first_section.pack(side=BOTTOM)