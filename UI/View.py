import tkinter as tk
from frames.ControlsFrame import ControlsFrame
from frames.SongFrame import SongFrame
from frames.SongBuilderFrame import SongBuilderFrame

class View(tk.Tk):
    def __init__(self):
        super().__init__()

        SCREEN_WIDTH = self.winfo_screenwidth()
        SCREEN_HEIGHT = self.winfo_screenheight()

        # set up window
        self.title('GuitarBot')
        self.geometry(f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # add main frames/components
        controls_frame = ControlsFrame(master=self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT * 0.20)
        controls_frame.grid(row=0, column=0)

        song_frame = SongFrame(master=self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT * 0.5)
        song_frame.grid(row=1, column=0)

        new_section_btn = tk.Button(self, text="New Section")
        new_section_btn.grid(row=2, column=0, pady=SCREEN_WIDTH*0.005)

        song_builder_frame = SongBuilderFrame(master=self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT * 0.25)
        song_builder_frame.grid(row=3, column=0)
    
    def start_mainloop(self):
        self.mainloop()