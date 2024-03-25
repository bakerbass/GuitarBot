import customtkinter as ctk
import tkinter as tk
from vis_entities.DraggableSectionLabel import DraggableSectionLabel
from frames.SongBuilderDragAndDropFrame import SongBuilderDragAndDropFrame

class SongBuilderFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, width, height):
        super().__init__(master, orientation='horizontal', width=width, height=height)

        self.width = width
        self.height = height
        self.section_labels = []

        self.drag_and_drop_canvas = SongBuilderDragAndDropFrame(master=self, width=width, height=height)
        # consider making each a button that simply appends draggable labels to end of existing list
        
        section_button_frame = tk.Frame(master=self.drag_and_drop_canvas)

        verse_btn = tk.Label(master=section_button_frame, text="verse", bg='navy blue', width=6, cursor='hand2')
        chorus_btn = tk.Label(master=section_button_frame, text="chorus", bg='navy blue', width=6, cursor='hand2')

        verse_btn.bind("<ButtonPress-1>", lambda event, arg='verse': self.add_section(event, arg))
        chorus_btn.bind("<ButtonPress-1>", lambda event, arg='chorus': self.add_section(event, arg))
        
        verse_btn.grid(row=0, column=0)
        chorus_btn.grid(row=0, column=1, padx=5)
        
        self.drag_and_drop_canvas.create_window(width/2.0, 15, anchor=tk.CENTER, window=section_button_frame)        
        
    def add_section(self, event, name):
        dsl = DraggableSectionLabel(name=name, mid_height_y=self.height/2.0)
        dsl.attach_at_end(canvas=self.drag_and_drop_canvas)

    