import numpy as np

from frontend.nodes.windows_fcts.window_fct import WindowFct
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class AveragedWindowFct(WindowFct, CNode):
    nodeName = "AveragedWindowFct"

    def __init__(
        self,
        window: CNode | None = None,
        avg_axis: int | tuple[int, ...] | None = None,
        render: bool = True,
        parent: CNode | None = None,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "data": {"io": "out"}
        }
        CNode.__init__(self, self.nodeName, terminals=terminals, render=render, parent=parent, alias=alias)
        WindowFct.__init__(self, window, self.aggregate)
        self.avg_axis = Element(self, "avg_axis", ElementValue(avg_axis))

    def aggregate(self, window_data):
        self.data.value[...] = np.mean(window_data, axis=self.avg_axis.value)
