class Human:

    def __init__(self):
        self.time = 0
        self.path = []
        self.is_safe = False

    def touch(self, path):
        self.time += 1
        self.path.append(path)
