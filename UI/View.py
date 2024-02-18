import customtkinter as ctk
from frames.RootFrame import RootFrame

class View(ctk.CTk):
    def __init__(self):
        # instantiate CTk application window
        super().__init__()

        self.title('GuitarBot')

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.geometry(f"{screen_width}x{screen_height}")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.root_frame = RootFrame(master=self, width=screen_width, height=screen_height, corner_radius=0, fg_color="transparent")
        self.root_frame.grid(row=0, column=0, sticky="nsew")
    
    def start_mainloop(self):
        self.mainloop()