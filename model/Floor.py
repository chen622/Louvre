from model.Item import Item


class Floor(Item):
    heuristic = float("inf")
    owner = None

    def __init__(self):
        pass
