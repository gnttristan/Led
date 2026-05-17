import numpy as np

from config import FREQ_BINS
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class RoutingNode(CNode):
    nodeName = "Routing"

    def __init__(
        self,
        operator_nodes: list[CNode] | None = None,
        input_data: np.ndarray = np.zeros(FREQ_BINS),
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "input_data": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render, alias=alias)

        self.operator_nodes = Element(self, "operator_nodes", ElementValue(operator_nodes or []))
        self.input_data = Element(self, "input_data", ElementValue(input_data))
        self.data = Element(self, "data", ElementValue(np.array(self.input_data.value, copy=True)))

    def c_update(self):
        self.data.value = np.array(self.input_data.value, copy=True)
