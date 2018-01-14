from copy import deepcopy

class LatestSentTracker(object):
    def __init__(self):
        self.targets = None

    def update(self, targets):
        self.targets = deepcopy(targets)

    def get_target(self):
        if self.targets:
            return self.targets[0]
        else:
            return None
