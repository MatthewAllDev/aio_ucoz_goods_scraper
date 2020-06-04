import sys
import math


class ProgressBar:
    def __init__(self, max_count: int):
        self.counter: int = 0
        self.max_count: int = max_count

    def inc(self, step: int = 1):
        self.counter += step

    def update_max_count(self, step: int = 1):
        self.max_count += step

    def reset(self):
        self.counter = 0

    def show(self):
        progress = self.counter / self.max_count
        sys.stdout.write(
            f"\rProgress: [{'#' * math.floor(progress * 25)} {'_' * math.floor((1 - progress) * 25)}] "
            f"{str(round(progress * 10000) / 100)}%")
        sys.stdout.flush()
