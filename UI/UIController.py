from UIModel import UIModel
from UIView import UIView

class UIController:
    def __init__(self, root):
        self.view = UIView(root)
        self.model = UIModel()