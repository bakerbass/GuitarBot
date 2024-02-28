import tkinter as tk
import customtkinter as ctk
from tkinter.constants import *
from frames.SectionFrame import SectionFrame
from frames.SectionLabelsFrame import SectionLabelsFrame

class SongFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, width, height):
        super().__init__(master, orientation='vertical', width=width, height=height)
        
        self.sections = []
        self.width = width
        self.height = height
        self.i = 0

        # add first section
        self.add_section()
        self.add_section()
        self.add_section()

            
    def add_section(self):
        labels = SectionLabelsFrame(master=self, width=self.width * 0.05, height=self.height * 0.2)
        section = SectionFrame(master=self, width=self.width, height=self.height * 0.33, time_signature="4/4")
        self.sections.append((labels, section))

        labels.grid(row=self.i, column=0)
        section.grid(row=self.i, column=1)
        self.i += 1