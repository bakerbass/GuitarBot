import tkinter as tk
import customtkinter as ctk
from tkinter.constants import *
from frames.SectionFrame import SectionFrame

class SongFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, width, height):
        super().__init__(master, orientation='vertical', width=width, height=height)

        # Add widgets to the frame
        for i in range(50):
            ctk.CTkLabel(self, text=f"Label {i}").grid(row=i, column=0)

            
    def add_section(self):
        self.first_section = SectionFrame(master=self, width=int(self.winfo_screenwidth() * 0.8), height=int(self.winfo_screenwidth() * 0.8))
        self.first_section.pack(side=BOTTOM)