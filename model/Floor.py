from model.Item import Item


class Floor(Item):
    heuristic = float("inf")
    owner = None

    def __init__(self):
        pass

    def set_heuristic(self, heuristic):
        if self.heuristic > heuristic:
            self.heuristic = heuristic