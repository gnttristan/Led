import numpy as np

from backend.updatable.updatable import AudioUpdatable
from config import FREQ_BINS
from frontend.components.elements import Interval
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.components.elements.textedit import TextEdit
from frontend.overrides.CNode import CNode


class BroadcastFractionNode(CNode, AudioUpdatable):
    nodeName = "BroadcastFractionNode"

    def __init__(
        self,
        input_data: np.ndarray = np.zeros(FREQ_BINS),
        fraction: float = 1.,
        interval_input: tuple[int, int] = (0, 1),
        input: float = 1,
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "input_data": {"io": "in"},
            "interval_input": {"io": "in"},
            "input": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render, alias=alias)

        self.input_data = Element(self, "input_data", ElementValue(input_data))
        self.fraction = TextEdit(self, "fraction", ElementValue(fraction))
        self.interval_input = Interval(self, "interval_input", ElementValue(interval_input))
        self.input = Element(self, "input", ElementValue(input))

        data_shape = (round(self.input_data.value.shape[0] * fraction), *self.input_data.value.shape[1:])
        self.data = Element(self, "data", ElementValue(np.zeros(data_shape)))

    def c_update(self):
        scale_position = np.clip(
            (self.input.value - self.interval_input.value[0]) / (self.interval_input.value[1] - self.interval_input.value[0]),
            0,
            1
        )

        window_length = int(self.fraction.value * self.input_data.value.shape[0])
        c = int(((1 - self.fraction.value) * scale_position * self.input_data.value.shape[0]).item())
        self.data.value[:] = self.input_data.value[c:c+window_length]

