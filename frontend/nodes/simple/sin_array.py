import numpy as np

from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.nodes.cnode import CNode


class SinArrayNode(CNode):
    nodeName = "SinArray"

    def __init__(
        self,
        cycle_length: int = 100,
        center: float = 0.5,
        offset: float = 0.1,
        render: bool = True,
    ) -> None:
        terminals = {
            "cycle_length": {"io": "in"},
            "center": {"io": "in"},
            "offset": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render)

        self.cycle_length = Element(self, "cycle_length", ElementValue(cycle_length))
        self.center = Element(self, "center", ElementValue(center))
        self.offset = Element(self, "offset", ElementValue(offset))
        self.data = Element(self, "data", ElementValue(np.zeros(int(self.cycle_length.value))))

        self.cycle_length.valueChanged.connect(self._refresh_data)
        self.center.valueChanged.connect(self._refresh_data)
        self.offset.valueChanged.connect(self._refresh_data)
        self._refresh_data()

    def _refresh_data(self, *_args) -> None:
        cycle_length = int(self.cycle_length.value)
        if cycle_length <= 0:
            self.data.value = np.zeros(0)
            return

        x = np.linspace(0, 2 * np.pi, cycle_length, endpoint=False)
        self.data.value = self.center.value + (self.offset.value * np.sin(x))
