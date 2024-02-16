import customtkinter as ctk

class View:
    def __init__(self):
        # instantiate root window
        self.root = ctk.CTk()
        self.root.title('GuitarBot')
        self.root.geometry("1200x800")

        # components

    def start_mainloop(self):
        self.root.mainloop()