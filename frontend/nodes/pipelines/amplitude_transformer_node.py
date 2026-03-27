import numpy as np
from scipy.signal import get_window

from backend.config import FFT_SIZE, FREQ_BINS, MAX_FREQUENCY, MIN_FREQUENCY
from backend.updatable.updatable import AudioUpdatable
from frontend.nodes.cnode import CNode

class AmplitudesNode(CNode, AudioUpdatable):
    nodeName = "Amplitudes"

    def __init__(
            self,
            input_data=np.zeros(FREQ_BINS),
            correlation_offset=None,
            correlation_step=None,
            powering=1,
            log=None
    ):
        self.input_data = input_data
        self.correlation_offset = correlation_offset
        self.correlation_step = correlation_step
        self.powering = powering
        self.log = log
        self.data = np.zeros(FREQ_BINS)

        terminals = {
            "input_data": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals)

    def c_update(self):
        self.buffer_to_amplitudes()

    def buffer_to_amplitudes(self):
        updated_amplitudes = self.input_data
        if self.log is not None:
            updated_amplitudes = np.power(updated_amplitudes, self.log)

        if self.correlation_offset is not None and self.correlation_step is not None:
            updated_amplitudes = np.correlate(
                updated_amplitudes,
                np.concatenate(
                    (
                        np.arange(1 - self.correlation_offset, 1, self.correlation_step),
                        np.arange(1, 1 - self.correlation_offset - self.correlation_step, - self.correlation_step)
                    )
                ),
                mode="same"
            )

        self.data[:] = updated_amplitudes
