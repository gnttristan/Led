import numpy as np

from backend.updatable.updatable import AudioUpdatable
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
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

        self.flag_changing_shape = False
        self.length = ExpSlider(self, "length", 1, 1000, ElementValue(length))
        self.input_data = Element(self, "input_data", ElementValue(input_data)) # Data to aggregate
        self.offset = Element(self, "offset", ElementValue(offset))
        input_shape = self.input_data.value.shape[0]
        self.data = Element(self, "data", ElementValue((np
            .repeat(init_value, self.length.value * input_shape)
            .reshape(self.length.value, input_shape))
        ))
        self.window_fcts = Element(self, "window_fcts", ElementValue([]))

        self.length.slider.valueChanged.connect(self.on_length_change)

    def on_length_change(self):
        self.flag_changing_shape = True

        int_length = int(self.length.value)
        if int_length < self.data.value.shape[0]:
            self.data.value = self.data.value[:int_length]
        else:
            self.data.value = np.vstack((
                self.data.value,
                np.zeros(((int_length - self.data.value.shape[0]), self.data.value.shape[1]))
            ))

        self.flag_changing_shape = False

    def c_update(self):
        self.roll()
        for window_fct in self.window_fcts.value:
            window_fct.aggregate(self.data.value)

    def roll(self):
        if self.flag_changing_shape:
            return
        try:
            self.data.value[:] = np.roll(self.data.value, -1, axis=0)
            self.data.value[-1] = np.roll(self.input_data.value, self.offset.value)
        except ValueError:
            pass
