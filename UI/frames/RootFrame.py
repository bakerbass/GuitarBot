import customtkinter as ctk
from frames.SongFrame import SongFrame

class RootFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.label = ctk.CTkLabel(self, text='GuitarBot')
        self.label.grid(row=0, column=0, padx=20)

        self.sections = SongFrame(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        self.sections.grid(row=1)
