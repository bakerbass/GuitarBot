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
        self.curr_id = 1

            
    def add_section(self):
        labels_frame = SectionLabelsFrame(master=self, id=self.curr_id, width=self.width * 0.05, height=self.height * 0.2)
        section_frame = SectionFrame(master=self, id=self.curr_id, width=self.width * 0.84, height=self.height * 0.21, time_signature="4/4")
        self.sections.append((section_frame, labels_frame))

        labels_frame.grid(row=self.i, column=0)
        section_frame.grid(row=self.i, column=1)
        self.i += 1
        self.curr_id += 1

        return section_frame.id, labels_frame.name