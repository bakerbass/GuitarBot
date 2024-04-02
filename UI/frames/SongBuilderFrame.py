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

        self.btn_dict = {}
        
        self.drag_and_drop_canvas.create_window(width/2.0, 15, anchor=tk.CENTER, window=self.section_button_frame)        
    
    def add_section_button(self, section_id, section_name):
        btn = tk.Label(master=self.section_button_frame, textvariable=section_name, bg='navy blue', width=6, cursor='hand2')

        btn.bind("<ButtonPress-1>", lambda event, arg=(section_id, section_name): self.add_draggable_section(event, arg))
        btn.pack(side='left', padx=5)

        self.btn_dict[section_id] = btn
        self.button_column += 1

    def remove_section_button_and_draggables(self, section_id):
        self.btn_dict[section_id].destroy()
        del self.btn_dict[section_id]
        
        i = 0
        while i < len(DraggableSectionLabel.existing_draggables_list):
            if DraggableSectionLabel.existing_draggables_list[i].section_id == section_id:
                DraggableSectionLabel.existing_draggables_list[i].destroy(None)
            i += 1

    def add_draggable_section(self, event, section_id_and_name):
        section_id, section_name = section_id_and_name
        dsl = DraggableSectionLabel(name=section_name, mid_height_y=self.height/2.0, section_id=section_id)
        dsl.attach_at_end(canvas=self.drag_and_drop_canvas)    