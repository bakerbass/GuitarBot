import customtkinter as ctk
import tkinter as tk
from vis_entities.DraggableSectionLabel import DraggableSectionLabel
from frames.SongBuilderDragAndDropFrame import SongBuilderDragAndDropFrame

class SongBuilderFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, width, height):
        super().__init__(master, orientation='horizontal', width=width, height=height)

        drag_and_drop_frame = SongBuilderDragAndDropFrame(master=self, width=width, height=height)
        verse = DraggableSectionLabel(name='verse')
        chorus = DraggableSectionLabel(name='chorus')
        bridge = DraggableSectionLabel(name='bridge')

        i = 700
        for curr in [verse, chorus, bridge]:
            curr.attach(drag_and_drop_frame, x=i,y=10)
            i += 80