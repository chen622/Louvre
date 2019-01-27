from abc import ABCMeta


class Item:
    pheromone = 0
    __mateclass__ = ABCMeta  # Means the class is an abstract class
