from types import SimpleNamespace

import numpy as np
from pyqtgraph.flowchart import Node

from backend.amplitudes.amplitudes import Amplitudes
from config import FFT_SIZE


class AmplitudesNode(Node):
    nodeName = "Amplitudes"

    def __init__(self, name):
        terminals = {
            "buffer": {"io": "in"},
            "amplitudes": {"io": "out"},
        }
        super().__init__(name, terminals=terminals)
        self.buffer_ref = SimpleNamespace(data=np.zeros(FFT_SIZE))
        self.pipeline = Amplitudes(
            buffer=self.buffer_ref,
            correlation_offset=0.3,
            correlation_step=0.05,
            powering=1,
            normalisation=True,
            log=0.7,
        )

    def process(self, buffer, display=True):
        del display
        if buffer is None:
            buffer = np.zeros(FFT_SIZE)

        self.buffer_ref.data[:] = buffer
        self.pipeline.update()
        return {"amplitudes": self.pipeline.data.copy()}

