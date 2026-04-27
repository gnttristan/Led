import numpy as np

from config import FFT_SIZE, FREQ_BINS, MAX_FREQUENCY, MIN_FREQUENCY
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.nodes.cnode import CNode
from frontend.nodes.pipelines.amplitudes.amplitude_transformer import AmplitudesTransformer


class LinearAmplitudesTransformerNode(CNode, AmplitudesTransformer):
    nodeName = "LinearAmplitudesTransformer"

    def __init__(
            self,
            input_data: np.ndarray = np.zeros(FREQ_BINS),
            correlation_offset: int | float | None = None,
            correlation_step: int | float | None = None,
            powering: float = 1.,
            log: float = 1.,
            amplitudes_level_fct: object = None,
            render: bool = True,
    ) -> None:
        terminals = {
            "input_data": {"io": "in"},
            "data": {"io": "out"},
        }

        CNode.__init__(self, self.nodeName, terminals, render=render)
        AmplitudesTransformer.__init__(self, powering=powering, log=log)

        self.input_data = Element(self, "input_data", ElementValue(input_data))
        self.correlation_offset = Element(self, "correlation_offset", ElementValue(correlation_offset))
        self.correlation_step = Element(self, "correlation_step", ElementValue(correlation_step))
        self.powering = Element(self, "powering", ElementValue(powering))
        self.log = Element(self, "log", ElementValue(log))
        self.data = Element(self, "data", ElementValue(np.zeros(FREQ_BINS)))
        self.amplitudes_level_fct = Element(self, "amplitudes_level_fct", amplitudes_level_fct)

    def c_update(self):
        self.transform_amplitudes(self.input_data.value)

    def transform_amplitudes(self, data):
        updated_amplitudes = data
        if self.correlation_offset.value is not None and self.correlation_step.value is not None:
            updated_amplitudes = np.correlate(
                updated_amplitudes,
                np.concatenate(
                    (
                        np.arange(1 - self.correlation_offset.value, 1, self.correlation_step.value),
                        np.arange(1, 1 - self.correlation_offset.value - self.correlation_step.value,
                                  - self.correlation_step.value)
                    )
                ),
                mode="same"
            )

        self.data.value[:] = super().transform_amplitudes(updated_amplitudes)
