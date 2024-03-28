import customtkinter as ctk
import tkinter as tk
from vis_entities.DraggableSectionLabel import DraggableSectionLabel
from frames.SongBuilderDragAndDropFrame import SongBuilderDragAndDropFrame

class SongBuilderFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, width, height):
        super().__init__(master, orientation='horizontal', width=width, height=height)

        self.width = width
        self.height = height

        self.drag_and_drop_canvas = SongBuilderDragAndDropFrame(master=self, width=width, height=height)
        self.section_button_frame = tk.Frame(master=self.drag_and_drop_canvas)
        self.button_column = 0
        
        self.drag_and_drop_canvas.create_window(width/2.0, 15, anchor=tk.CENTER, window=self.section_button_frame)        
    
    def add_section_button(self, id, section_name):
        btn = tk.Label(master=self.section_button_frame, textvariable=section_name, bg='navy blue', width=6, cursor='hand2')

        btn.bind("<ButtonPress-1>", lambda event, arg=(id, section_name): self.add_draggable_section(event, arg))
        btn.grid(row=0, column=self.button_column, padx=5)

        self.button_column += 1

    def remove_section_button(self, id):
        pass

    def add_draggable_section(self, event, id_and_section_name):
        id, section_name = id_and_section_name
        dsl = DraggableSectionLabel(name=section_name, mid_height_y=self.height/2.0)
        dsl.attach_at_end(canvas=self.drag_and_drop_canvas)    