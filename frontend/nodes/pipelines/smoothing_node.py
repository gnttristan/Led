import numpy as np
from pyqtgraph.flowchart import Node

from backend.pipelines.transforms.smoothing import SmoothingPipeline
from config import FREQ_BINS


class SmoothingNode(Node):
    nodeName = "Smoothing"

    def __init__(self, name, length=10, offset=0):
        terminals = {
            "data": {"io": "in"},
            "smoothed": {"io": "out"},
        }
        super().__init__(name, terminals=terminals)
        self.input_data = np.zeros(FREQ_BINS)
        self.pipeline = SmoothingPipeline(
            input_value=self.input_data,
            length=length,
            avg_axis=0,
            offset=offset,
        )

    def process(self, data, display=True):
        del display
        if data is None:
            data = np.zeros(FREQ_BINS)

        self.input_data[:] = data
        self.pipeline.update()
        return {"smoothed": self.pipeline.data.copy()}

