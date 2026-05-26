import numpy as np
from scipy.signal import butter

from config import SAMPLE_RATE, FFT_SIZE
from frontend.components.elements.dials import LinearDial
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode
from frontend.nodes.pipelines.auditory.filter.filter import Filter


class BandFilterPipelineNode(CNode, Filter):
    nodeName = "BandFilter"

    def __init__(
        self,
        buffer_data: np.ndarray = np.zeros(0),
        lowcut: float = 500.0,
        highcut: float = 3000.0,
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "buffer_data": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render, alias=alias)
        self.buffer_data = Element(self, "buffer_data", ElementValue(buffer_data))
        Filter.__init__(self, buffer_data=self.buffer_data)

        self.lowcut = LinearDial(self, "lowcut", 1, 1000, ElementValue(lowcut))
        self.highcut = LinearDial(self, "highcut", 1, 5000, ElementValue(highcut))
        self.data = Element(self, "data", ElementValue(np.zeros(FFT_SIZE)))

    @staticmethod
    def butter_bandpass(lowcut, highcut, fs, order=1):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        return butter(order, [low, high], btype="band")

    def filter_coefficients(self, fs, order=1):
        return self.butter_bandpass(self.lowcut.value, self.highcut.value, fs, order)

    def c_update(self):
        self.data.value[:] = self.apply_filter(self.buffer_data.value, SAMPLE_RATE)
