import numpy as np

from backend.updatable.updatable import AudioUpdatable
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.components.sliders import LinearSlider
from frontend.nodes.cnode import CNode


class AmplitudesLevelFunction(CNode, AudioUpdatable):
    nodeName = "AmplitudeLevelFunction"

    def __init__(
        self,
        number_points,
        offset=0.85,
        drop=0.6,
        drop_center=75,
        drop_width=10,
        rise=0.15,
        rise_center=225,
        rise_width=10,
        render=True
    ):
        terminals = {
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render)

        self.arange = Element(self, "arange", ElementValue(np.arange(number_points)))
        self.data = Element(self, "data", ElementValue(np.zeros(number_points)), link_terminal=False)

        self.offset = LinearSlider(self, "offset", 0.0, 1.5, offset)

        self.drop = LinearSlider(self, "drop", 0.0, 1.0, drop)
        self.drop_center = LinearSlider(self, "drop_center", 0, number_points // 2, drop_center)
        self.drop_width = LinearSlider(self, "drop_width", 1, max(10, number_points // 5), drop_width)

        self.rise = LinearSlider(self, "rise", 0.0, 0.5, rise)
        self.rise_center = LinearSlider(self, "rise_center", number_points // 2, number_points, rise_center)
        self.rise_width = LinearSlider(self, "rise_width", 1, max(10, number_points // 5), rise_width)

    def fct(self, amplitudes_data):
        self.data.value[:] = amplitudes_data * (
            self.offset.value
            - self.drop.value / (1 + np.exp(-(self.arange.value - self.drop_center.value) / self.drop_width.value))
            + self.rise.value / (1 + np.exp(-(self.arange.value - self.rise_center.value) / self.rise_width.value))
        )
        return self.data.value
