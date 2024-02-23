import customtkinter as ctk
import tkinter as tk

class SongBuilderFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, width, height):
        super().__init__(master, orientation='horizontal', width=width, height=height)

        # Add widgets to the frame
        for i in range(50):
            ctk.CTkLabel(self, text=f"Label {i}").grid(row=0, column=i)