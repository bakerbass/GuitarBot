from View import View

# model handles the business logic for the UI -> calls UIParse.py methods
class Model:
    def __init__(self, view: View):
        self.view = view
