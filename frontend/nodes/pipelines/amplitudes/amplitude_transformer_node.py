import numpy as np

from config import FFT_SIZE, FREQ_BINS, MAX_FREQUENCY, MIN_FREQUENCY
from backend.updatable.updatable import AudioUpdatable
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.nodes.cnode import CNode

class AmplitudesTransformerNode(CNode, AudioUpdatable):
    nodeName = "AmplitudesTransformer"

    def __init__(
            self,
            input_data=np.zeros(FREQ_BINS),
            correlation_offset=None,
            correlation_step=None,
            powering=1,
            log=None,
            amplitudes_level_fct=None,
    ):
        terminals = {
            "input_data": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals)
        self.input_data = Element(self, "input_data", ElementValue(input_data))
        self.correlation_offset = Element(self, "correlation_offset", ElementValue(correlation_offset))
        self.correlation_step = Element(self, "correlation_step", ElementValue(correlation_step))
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

        if self.correlation_offset.value is not None and self.correlation_step.value is not None:
            updated_amplitudes = np.correlate(
                updated_amplitudes,
                np.concatenate(
                    (
                        np.arange(1 - self.correlation_offset.value, 1, self.correlation_step.value),
                        np.arange(1, 1 - self.correlation_offset.value - self.correlation_step.value, - self.correlation_step.value)
                    )
                ),
                mode="same"
            )
            
        if self.amplitudes_level_fct.value is not None:
            updated_amplitudes = self.amplitudes_level_fct.value.fct(updated_amplitudes)

        self.data.value[:] = updated_amplitudes
