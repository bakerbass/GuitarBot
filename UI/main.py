from controller import Controller
from model import Model
from view import View

def main():
    view = View()
    model = Model()
    controller = Controller(view, model)
    controller.start()

# run this script to start the UI
if __name__ == "__main__":
    main()