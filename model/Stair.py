from model.Item import Item


class Stair(Item):
    WAITTIME = 2
    current = WAITTIME
    owner = None

    def __init__(self):
        pass
