import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from frames.SectionFrame import SectionFrame

class SongFrame(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=False)
        
    #     self.add_section() # first section

            
    # def add_section(self):
    #     self.first_section = SectionFrame(master=self, width=int(self.winfo_screenwidth() * 0.8), height=300, orientation='horizontal')
    #     self.first_section.grid(row=1, column=0, padx=20)