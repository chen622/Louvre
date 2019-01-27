
ALPHA = 1
BETA = 1


class Item:

    def __init__(self):
        self.heuristic = float('inf')
        self.pheromone = 1
        self.owner = None
        self.cache = 0
        self.check_cache = [float('inf'), 0]

    def get_probability(self):
        if self.check_cache[0] != self.heuristic or self.check_cache[1] != self.pheromone:
            self.check_cache[0] = self.heuristic
            self.check_cache[1] = self.pheromone
            if self.heuristic == 0:
                self.cache = float('inf')
            else:
                self.cache = ((1 / self.heuristic) ** BETA) * (self.pheromone ** ALPHA)
        return self.cache
