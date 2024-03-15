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

        # for i in range (0, len(self.section_labels)):
        #     self.section_labels[i][1] = self.section_labels[i][1] - 30
        #     self.section_labels[i][0].attach(canvas=self.drag_and_drop_canvas, x=self.section_labels[i][1], y=self.height/2.0)
        
        dsl.attach(canvas=self.drag_and_drop_canvas, x=self.width/2.0 + 30, y=self.height/2.0)
        
        # self.section_labels.append((dsl, self.width/2.0 + 30))

        # need to track existing ones and left shift them?

    