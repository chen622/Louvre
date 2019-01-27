from model.Item import Item


class Floor(Item):

    def __init__(self):
        Item.__init__(self)
        self.heuristic = float("inf")

    def set_heuristic(self, heuristic):
        if self.heuristic > heuristic:
            self.heuristic = heuristic