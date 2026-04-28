import numpy as np

from config import FFT_SIZE, FREQ_BINS
from backend.updatable.updatable import AudioUpdatable
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class OutboundsUpFctNode(CNode, AudioUpdatable):
    nodeName = "OutboundsUpFct"

    def __init__(
        self,
        y: float = 1,
        outbound_len: float = 0.25,
        length: int = FREQ_BINS,
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "y": {"io": "in"},
            "outbound_len": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render, alias=alias)

        self.y = Element(self, "y", ElementValue(y))
        self.outbound_len = Element(self, "outbound_len", ElementValue(outbound_len))
        self.length = Element(self, "length", ElementValue(length))
        self.data = Element(self, "data", ElementValue(np.zeros(self.length.value)))

    def c_update(self):
        gap = (1 / self.outbound_len.value) / 2
        half_part = np.linspace(self.y.value, self.y.value - gap, self.length.value // 2).flatten()
        self.data.value[:] = np.maximum(
            np.concatenate(((h:=half_part), h[::-1])),
            0
        )






