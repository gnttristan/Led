from typing import Type

from backend.updatable.updatable import AudioUpdatable

import numpy as np

from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.nodes.cnode import CNode
from frontend.nodes.window.window import WindowNode
from backend.windows_fcts.window_fct import WindowFct
from frontend.nodes.windows_fcts.averaged_window_fct import AveragedWindowFct


class SmoothingNode(CNode, AudioUpdatable):
    nodeName = "Smoothing"

    def __init__(
            self,
            input_value: np.ndarray = np.zeros(0),
            length: int = 0,
            window_function: WindowFct | None = None,
            avg_axis: int | tuple[int, ...] | None = 0,
            offset: int = 0,
            render: bool = True,
    ) -> None:
        terminals = {
            "input_value": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render)

        self.input_value = Element(self, "input_value", ElementValue(input_value))
        self.avg_axis = avg_axis

        self.length = Element(self, "length", ElementValue(length))
        self.window = Element(
            self,
            "window",
            WindowNode(input_data=self.input_value, length=self.length.value, offset=offset, render=render, is_child=True),
        )

        window_function = Element(self, "window_function",
            ElementValue(AveragedWindowFct(self.window.value, avg_axis=avg_axis, is_child=True))
            if not window_function
            else window_function
        )
        self.average_window = window_function

        self.data = Element(self, "data", ElementValue(np.zeros(self.input_value.value.shape[-1])))
        self.length.valueChanged.connect(self._sync_length)

    def _sync_length(self, value):
        self.data.value = np.zeros(self.input_value.value.shape[-1])
        self.window.value.length.value = value
        self.average_window.value.window.value = self.window.value

    def c_update(self):
        if not hasattr(self, "average_window"):
            return
        try:
            self.data.value[...] = self.average_window.value.data
        except Exception as e:
            pass

    # def connected(self, localTerm, remoteTerm):
    #     super().connected(localTerm, remoteTerm)
