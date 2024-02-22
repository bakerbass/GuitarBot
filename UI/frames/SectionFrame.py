import tkinter as tk
from tkinter.constants import *
from frames.BarFrame import BarFrame

class SectionFrame(tk.Canvas):
    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, *args, **kwargs)

        self.vscrollbar = tk.Scrollbar(self, orient=HORIZONTAL)
        self.vscrollbar.grid(row=0, column=0)
        # add widgets onto the frame...
        self.bar = BarFrame(master=self)
        self.bar.grid(row=0, column=0, padx=20)

        self.bar = BarFrame(master=self)
        self.bar.grid(row=0, column=0, padx=20)

    def add_bar(self):
        self.bar = BarFrame(master=self)
        self.bar.grid(row=0, column=1, padx=20)
