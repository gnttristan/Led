import numpy as np

from backend.updatable.updatable import AudioUpdatable
from frontend.components.element.element import Element
from frontend.components.sliders import ExpSlider
from frontend.nodes.cnode import CNode


class WindowNode(CNode, AudioUpdatable):
    nodeName = "Window"

    def __init__(self, input_data, length, init_value=0., offset=0, render=True):
        terminals = {
            "input_data": {"io": "in"},
            "data": {"io": "out"}
        }

        super().__init__(self.nodeName, terminals, render)

        self.length = ExpSlider(self, "length", 1, 1000, value=length)
        self.input_data = Element(self, "input_data", input_data) # Data to aggregate
        self.offset = Element(self, "offset", offset)
        self.data = Element(self, "data", (np
            .repeat(init_value, self.length.value * input_data.shape[0])
            .reshape(self.length.value, input_data.shape[0]))
        )
        self.window_fcts = Element(self, "window_fcts", [])

    def c_update(self):
        self.roll()
        for window_fct in self.window_fcts.value:
            window_fct.aggregate(self.data.value)

    def roll(self):
        if self.input_data.value.shape[0] != self.data.value.shape[1]:
            pass
            # self.data.reshape(self.length, self.input_data.shape[0])
        self.data.value[:] = np.roll(self.data.value, -1, axis=0)
        self.data.value[-1] = np.roll(self.input_data.value, self.offset.value)
