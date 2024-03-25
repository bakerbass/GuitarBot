class Section:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.left_arm = []
        self.right_arm = []

        # add hardcoded left_arm, right_arm data for now
        # time signature assumed to be 4/4
        self.left_arm = [['C', 'G', 'D', 'F'], ['C', 'Am', 'G', 'F']]
        self.right_arm = [['d', '', 'd', '', 'u', '', 'u', ''], ['d', 'u', 'd', 'u', 'd', 'u', 'd', 'u']]

    def clear(self):
        self.left_arm = []
        self.right_arm = []
