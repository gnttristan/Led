from backend.updatable.updatable import AudioUpdatable

import numpy as np

from backend.window.window import Window
from backend.windows_fcts.averaged_window_fct import AveragedWindowFct
from frontend.nodes.cnode import CNode


class SmoothingNode(CNode, AudioUpdatable):
    nodeName = "Smoothing"

    def __init__(
            self,
            input_value,
            length,
            avg_axis=None,
            offset=0
    ):
        self.input_value = input_value
        self.length = length
        self.avg_axis = avg_axis

        self.window = Window(input_data=self.input_value, length=length, offset=offset)
        self.average_window = AveragedWindowFct(self.window, avg_axis=avg_axis)
        self.data = np.zeros(self.average_window.data.shape[-1])

        terminals = {
            "input_value": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals)

    def c_update(self):
        self.window.c_update()
        self.data[...] = self.average_window.data

