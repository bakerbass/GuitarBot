import customtkinter as ctk
from frames.BarFrame import BarFrame

class SectionFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color='blue')
        # add widgets onto the frame...
        self.bar = BarFrame(master=self)
        self.bar.grid(row=0, column=0, padx=20)

        self.bar = BarFrame(master=self)
        self.bar.grid(row=0, column=0, padx=20)

    def add_bar(self):
        self.bar = BarFrame(master=self)
        self.bar.grid(row=0, column=0, padx=20)
