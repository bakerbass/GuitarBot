from Controller import Controller
from Model import Model
from View import View

# run this script to start the UI
def main():
    view = View()
    model = Model()
    controller = Controller(view, model)
    controller.start()

if __name__ == "__main__":
    main()