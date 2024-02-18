from Model import Model
from View import View

class Controller:
    def __init__(self, view: View, model: Model):
        self.view = view
        self.model = model

        self._create_event_bindings

    def _create_event_bindings():
        pass

    def start(self):
        self.view.start_mainloop()

