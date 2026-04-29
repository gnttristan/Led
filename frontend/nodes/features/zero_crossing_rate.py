import numpy as np

from backend.pipelines.pipeline import AudioPipeline
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class ZeroCrossingRateNode(CNode, AudioPipeline):
    nodeName = "ZeroCrossingRate"

    def __init__(self, buffer_data=np.zeros(0), render: bool = True, alias: str | None = None) -> None:
        terminals = {
            "buffer_data": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render, alias=alias)
        self.buffer_data = Element(self, "buffer_data", ElementValue(buffer_data))
        self.data = Element(self, "data", ElementValue(np.zeros(1)))

    def c_update(self):
        data = np.asarray(self.buffer_data.value, dtype=float)
        if data.ndim > 1:
            data = np.mean(data, axis=-1)
        data = data.reshape(-1)
        if data.size < 2:
            self.data.value[...] = 0.0
            return
        signs = np.signbit(data)
        self.data.value[...] = np.count_nonzero(signs[1:] != signs[:-1]) / (data.size - 1)
