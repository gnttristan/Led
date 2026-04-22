from itertools import pairwise

import numpy as np

from config import FFT_SIZE, FREQ_BINS, MAX_FREQUENCY, MIN_FREQUENCY
from backend.updatable.updatable import AudioUpdatable
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.nodes.cnode import CNode

class AmplitudesTransformerNode(CNode, AudioUpdatable):
    nodeName = "AmplitudesTransformer"

    def __init__(
        self,
        input_data: np.ndarray = np.zeros(FREQ_BINS),
        correlation_offset: int | float | None = None,
        correlation_step: int | float | None = None,
        correlation_weight_min: int | float = 50,
            powering: int | float = 1,
            log: int | float | None = None,
            amplitudes_level_fct: object = None,
            render: bool = True,
    ) -> None:
        terminals = {
            "input_data": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render)
        self.input_data = Element(self, "input_data", ElementValue(input_data))
        self.correlation_offset = Element(self, "correlation_offset", ElementValue(correlation_offset))
        self.correlation_step = Element(self, "correlation_step", ElementValue(correlation_step))
        self.correlation_weight_min = Element(self, "correlation_weight_min", ElementValue(correlation_weight_min))
        self.powering = Element(self, "powering", ElementValue(powering))
        self.log = Element(self, "log", ElementValue(log))
        self.data = Element(self, "data", ElementValue(np.zeros(FREQ_BINS)))
        self.amplitudes_level_fct = Element(self, "amplitudes_level_fct", amplitudes_level_fct)

    def c_update(self):
        self.transform_amplitudes()

    def transform_amplitudes(self):
        updated_amplitudes = self.input_data.value
        if self.log.value is not None:
            updated_amplitudes = np.power(updated_amplitudes, self.log.value)

        # if self.correlation_offset.value is not None and self.correlation_step.value is not None:
        #     n = updated_amplitudes.size
        #     radius = np.maximum(1, (np.linspace(1, self.correlation_weight_min.value, n) / 10).astype(int))
        #
        #     windows = [updated_amplitudes[max(0, i - r):min(n, i + r + 1)] for i, r in enumerate(radius)]
        #     sizes = [x.size for x in windows]
        #     groups_weights_repartition = [1 + (2 * np.linspace(0, 1, s) - 1) / 2 for s in sizes]
        #     norm_gwr = [g / np.sum(g) for g in groups_weights_repartition]
        #     updated_amplitudes = np.array([np.sum(w/(g+1e-12)) for w, g in zip(windows, norm_gwr)])

        if self.amplitudes_level_fct.value is not None:
            updated_amplitudes = self.amplitudes_level_fct.value.fct(updated_amplitudes)

        self.data.value[:] = updated_amplitudes
