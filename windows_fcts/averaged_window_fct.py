import numpy as np

from windows_fcts.window_fct import WindowFct

class AveragedWindowFct(WindowFct):
    def __init__(self, window, avg_axis=None):
        super().__init__(window, self.aggregate)
        self.window = window
        self.avg_axis = avg_axis

    def aggregate(self, window_data):
        self.data = np.mean(window_data, axis=self.avg_axis)

