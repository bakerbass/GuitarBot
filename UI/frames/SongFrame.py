import tkinter as tk
import customtkinter as ctk
from tkinter.constants import *
from frames.SectionFrame import SectionFrame

class SongFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, width, height):
        super().__init__(master, orientation='vertical', width=width, height=height)
        
        self.sections = []
        self.width = width
        self.height = height

        # add first section
        self.add_section()
        
        self.add_section()
        self.add_section()
        self.add_section()

            
    def add_section(self):
        new_section = SectionFrame(master=self, width=self.width, height=self.height * 0.33, timeSignature="4/4")
        self.sections.append(new_section)
        new_section.pack(side=BOTTOM)