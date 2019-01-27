from model.Item import Item


class Exit(Item):

    def __init__(self):
        Item.__init__(self)
        self.heuristic = 0
        self.safe_humans = []

    def out(self, human):
        self.safe_humans.append(human)
