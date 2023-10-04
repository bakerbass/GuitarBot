import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *

# GuitarBot UI
sections = []
sectionsDict = {}

rootWindow = tk.Tk(className=' GuitarBot')
rootWindow.geometry("1300x600")

mainFrame = Frame(rootWindow)
scrollbar = Scrollbar(mainFrame, orient="vertical")
scrollbar.pack(side="right", fill=Y)

#Add Entry Widgets
Label(mainFrame, text= "Username").pack()
username= Entry(mainFrame, width= 20)
username.pack()
Label(mainFrame, text= "password").pack()
password= Entry(mainFrame, show="*", width= 15)
password.pack()
Label(mainFrame, text= "Email Id").pack()
email= Entry(mainFrame, width= 15)
email.pack()


mainFrame.pack()
rootWindow.mainloop()