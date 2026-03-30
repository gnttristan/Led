import numpy as np

from backend.windows_fcts.window_fct import WindowFct
from frontend.nodes.cnode import CNode


class AveragedWindowFct(CNode, WindowFct):
    def __init__(self, window, avg_axis=None):
        super().__init__(window, self.aggregate)
        self.window = window
        self.avg_axis = avg_axis

    def aggregate(self, window_data):
        self.data = np.mean(window_data, axis=self.avg_axis)

