from backend.updatable.updatable import AudioUpdatable

import numpy as np

from backend.window.window import Window
from backend.windows_fcts.averaged_window_fct import AveragedWindowFct
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.nodes.cnode import CNode
from frontend.nodes.window.window import WindowNode


class SmoothingNode(CNode, AudioUpdatable):
    nodeName = "Smoothing"

    def __init__(
            self,
            input_value,
            length,
            window_function=AveragedWindowFct,
            avg_axis=None,
            offset=0
    ):
        terminals = {
            "input_value": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals)

        self.input_value = Element(self, "input_value", ElementValue(input_value))
        self.avg_axis = avg_axis

        self.length = ElementValue(length)
        self.window = Element(
            self,
            "window",
            ElementValue(WindowNode(input_data=self.input_value, length=self.length, offset=offset)),
        )
        self.average_window = window_function(self.window.value, avg_axis=avg_axis)
        self.data = Element(self, "data", ElementValue(np.zeros(self.average_window.data.shape[-1])))

    def c_update(self):
        self.data.value[:] = self.average_window.data

