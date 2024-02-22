import tkinter as tk

from Model import Model
from View import View
from Controller import Controller

def main():
    model = Model()

    app = tk.Tk(className=' GuitarBot')
    view = View(app)
    view.pack()

    controller = Controller(view, model)
    controller.start()

# run this script to start the UI
if __name__ == "__main__":
    main()