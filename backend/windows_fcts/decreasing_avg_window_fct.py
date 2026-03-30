import numpy as np

from backend.windows_fcts.window_fct import WindowFct

class DecreasingAvgWindowFct(WindowFct):
    def __init__(self, window, avg_axis=None):
        super().__init__(window, self.aggregate)
        self.window = window
        self.avg_axis = avg_axis

    def aggregate(self, window_data):
        weights = (np.arange(window_data.shape[0]) + 1)[::-1] / window_data.shape[0]
        total_weight = np.sum(weights)
        self.data = np.sum((window_data * weights[:, None]) / total_weight, axis=self.avg_axis)

