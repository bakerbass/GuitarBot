from controller import Controller
from model import Model
from view import View

# run this script to start the UI
def main():
    view = View()
    model = Model(view)
    controller = Controller(view, model)
    controller.start()

if __name__ == "__main__":
    main()