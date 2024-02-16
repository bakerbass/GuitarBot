import customtkinter as ctk
from components.RootFrame import RootFrame

class View(ctk.CTk):
    def __init__(self):
        # instantiate CTk application window
        super().__init__()

        self.title('GuitarBot')
        self.geometry("1200x800")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.root_frame = RootFrame(master=self, width=300, height=200, corner_radius=0, fg_color="transparent")
        self.root_frame.grid(row=0, column=0, sticky="nsew")
    
    def start_mainloop(self):
        self.mainloop()