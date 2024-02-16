import customtkinter as ctk

class RootFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.label = ctk.CTkLabel(self, text='test label')
        self.label.grid(row=0, column=0, padx=20)