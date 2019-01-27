from model.Item import Item


class Exit(Item):
    heuristic = 0
    safeHumans = []

    def __init__(self):
        pass

    def out(self, human):
        self.safeHumans.append(human)
