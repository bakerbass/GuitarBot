import customtkinter as ctk
from frames.SectionFrame import SectionFrame

class SongFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.add_section() # first section

            
    def add_section(self):
        self.first_section = SectionFrame(master=self, width=int(self.winfo_screenwidth() * 0.8), height=300, orientation='horizontal')
        self.first_section.grid(row=1, column=0, padx=20)