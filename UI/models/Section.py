class Section:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.left_arm = []
        self.right_arm = []

        # # add hardcoded left_arm, right_arm data for now
        # # time signature assumed to be 4/4
        # self.left_arm = [['C M', 'G M', 'D M', 'F M'], ['C M', 'Am M', 'G M', 'F M']]
        # self.right_arm = [['D', '', 'D', '', 'U', '', 'U', ''], ['D', 'U', 'D', 'U', 'D', 'U', 'D', 'U']]

    def clear(self):
        self.left_arm = []
        self.right_arm = []
