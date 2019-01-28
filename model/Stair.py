from model.Item import Item


class Stair(Item):
    WAIT_TIME = 2

    def __init__(self, toward):
        Item.__init__(self)
        self.toward = toward
        self.heuristic = float("inf")
        self.h_toward = -1  # Up to down is 0,down to up is 1
        self.current = self.WAIT_TIME
        self.is_pass = False

    def is_up_to_down(self, heuristic):
        self.heuristic = heuristic
        self.h_toward = 0

    def is_down_to_up(self, heuristic):
        self.heuristic = heuristic
        self.h_toward = 1

    def set_heuristic(self, heuristic):
        if self.heuristic > heuristic:
            self.heuristic = heuristic
            return True
        return False
    def touch(self):
        self.current -= 1
        if self.current < 0:
            return True
        else:
            return False
