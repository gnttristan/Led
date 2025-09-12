import numpy as np

class WindowFct:
    def __init__(self, window, aggregation):
        self.data = np.zeros(1)
        self.aggregation = aggregation

        window.window_fcts.append(self)
