import numpy as np
from pyqtgraph.flowchart import Node

from backend.pipelines.transforms.value_transformer import ValueTransformerPipeline
from config import FREQ_BINS


class ValueTransformNode(Node):
    nodeName = "ValueTransform"

    def __init__(self, name):
        terminals = {
            "data": {"io": "in"},
            "alpha": {"io": "out"},
        }
        super().__init__(name, terminals=terminals)
        self.input_data = np.zeros(FREQ_BINS)
        self.pipeline = ValueTransformerPipeline(
            input_value=self.input_data,
            input_value_interval=[0, 1],
            output_value_interval=[0, 255],
            power=1.8,
        )

    def c_update(self, data, display=True):
        del display
        if data is None:
            data = np.zeros(FREQ_BINS)

        self.input_data[:] = np.clip(np.asarray(data), 0, 1)
        self.pipeline.c_update()
        return {"alpha": self.pipeline.output_value.copy()}

