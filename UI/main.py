import tkinter as tk

from Model import Model
from View import View
from Controller import Controller

def main():
    view = View()
    model = Model()
    controller = Controller(view, model)
    controller.start()

# run this script to start the UI
if __name__ == "__main__":
    main()