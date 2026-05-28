import numpy as np

from backend.updatable.updatable import AudioUpdatable
from config import FREQ_BINS
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class AvgFrequenciesNode(CNode, AudioUpdatable):
    nodeName = "AvgFrequencies"

    def __init__(
        self,
        input_frequencies: np.ndarray = np.zeros(FREQ_BINS),
        input_amplitudes: np.ndarray = np.zeros(FREQ_BINS),
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "input_frequencies": {"io": "in"},
            "input_amplitudes": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render, alias=alias)

        self.input_frequencies = Element(self, "input_frequencies", ElementValue(input_frequencies))
        self.input_amplitudes = Element(self, "input_amplitudes", ElementValue(input_amplitudes))
        self.data = Element(self, "data", ElementValue(np.zeros(1)))

    def c_update(self):
        self.data.value[...] = np.sum(
            (self.input_amplitudes.value * self.input_frequencies.value)
            / np.sum(self.input_amplitudes.value + 1e-12)
        )
