import numpy as np

from backend.rainbow.config import RAINBOW_INV_FRACTION, ROLL_SPEED
from backend.rainbow.rainbow import Rainbow
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.components.dials import LinearDial
from frontend.nodes.cnode import CNode


class GradiantRainbowNode(Rainbow, CNode):
    nodeName = "GradiantRainbow"
    def __init__(
            self,
            roll_speed=ROLL_SPEED,
            inv_fraction=RAINBOW_INV_FRACTION
    ):
        terminals = {
            "data": {"io": "out"},
        }

        CNode.__init__(self, self.nodeName, terminals=terminals)

        self.inv_fraction = LinearDial(self, "inv_fraction", 0, 1, inv_fraction)
        Rainbow.__init__(self, self.inv_fraction.value)
        self.roll_speed = LinearDial(self, "roll_speed", 0, 10, roll_speed)
        self.data = Element(self, "data", ElementValue(self.data))


    def c_update(self):
        super().c_update()
        self.roll_rainbow()

    def roll_rainbow(self):
        self.data.value[:] = np.roll(self.data.value, int(self.roll_speed.value), axis=0)

