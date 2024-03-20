
import time

class TimeCost:

    def __init__(self):

        self.preCounter = time.perf_counter()

    def countDown(self):
        c = time.perf_counter()
        r = c - self.preCounter
        print("{} - {} = {}".format(c, self.preCounter, r))
        self.preCounter = c
        return r

