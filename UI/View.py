import tkinter as tk
from frames.RootFrame import RootFrame

class View(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        master.geometry(f'{screen_width}x{screen_height}')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        master.label = tk.Label(master=self, text='The quick brown fox jumped over the lazy dog')
        master.label.grid(row=0, column=0, padx=20)

        master.root_frame = RootFrame(master=self, width=screen_width, height=screen_height)
        master.root_frame.grid(row=0, column=0, sticky="nsew")
    
    def start_mainloop(self):
        self.mainloop()