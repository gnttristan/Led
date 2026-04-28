import numpy as np

from backend.windows_fcts.window_fct import WindowFct
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class AveragedWindowFct(WindowFct, CNode):
    nodeName = "AveragedWindowFct"

    def __init__(
        self,
        window: CNode,
        avg_axis: int | tuple[int, ...] | None = None,
        render: bool = True,
        is_child: bool = False
    ) -> None:
        terminals = {
            "data": {"io": "out"}
        }
        WindowFct.__init__(self, window, self.aggregate)
        CNode.__init__(self, self.nodeName, terminals=terminals, render=render, is_child=is_child)
        self.window = Element(self, "window", ElementValue(window))
        self.avg_axis = Element(self, "avg_axis", ElementValue(avg_axis))

    def aggregate(self, window_data):
        self.data = np.mean(window_data, axis=self.avg_axis.value)
        # self.data = np.ones(window_data.shape[-1])
