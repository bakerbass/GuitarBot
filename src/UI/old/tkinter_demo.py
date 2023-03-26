import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox

window = tk.Tk(className='GuitarBot Interface')
window.geometry("500x400")
noteFrame = Frame(window)
pitchFrame = Frame(window)
typeFrame = Frame(window)
noteFrame.pack()
pitchFrame.pack()
typeFrame.pack()

notes = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G"
]

pitches = [
    "♮",
    "#",
    "♭"
]

types = [
    "Maj",
    "min"
]

noteMenu = OptionMenu(noteFrame, StringVar(), "C", *notes)
noteLabel = Label(noteFrame, text="Note: ")
pitchMenu = OptionMenu(pitchFrame, StringVar(), "♮", *pitches)
pitchLabel = Label(pitchFrame, text="Pitch: ")
typeMenu = OptionMenu(typeFrame, StringVar(), "Maj", *types)
typeLabel = Label(typeFrame, text="Type: ")

noteLabel.pack(side=LEFT)
noteMenu.pack(side=RIGHT)
pitchLabel.pack(side=LEFT)
pitchMenu.pack(side=RIGHT)
typeLabel.pack(side=LEFT)
typeMenu.pack(side=RIGHT)

def send_msg():
    tkinter.messagebox.showinfo("Alert", "Chord sent to GuitarBot.")

send = Button(window, text="Send", width=4, command=send_msg)
send.pack(pady=12)

window.mainloop()