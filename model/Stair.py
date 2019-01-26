from model.Item import Item


class Stair(Item):
    heuristic = float("inf")
    toward = -1  # Up to down is 0,down to up is 1
    h_toward = -1 # Up to down is 0,down to up is 1
    WAIT_TIME = 2
    current = WAIT_TIME
    isPass = False
    owner = None

    def __init__(self, toward):
        self.toward = toward

    def is_up_to_down(self, heuristic):
        self.heuristic = heuristic
        self.h_toward = 0

    def is_down_to_up(self, heuristic):
        self.heuristic = heuristic
        self.h_toward = 1

    def set_heuristic(self, heuristic):
        if self.heuristic > heuristic:
            self.heuristic = heuristic
