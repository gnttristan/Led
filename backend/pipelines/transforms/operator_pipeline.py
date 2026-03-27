import numpy as np

from backend.pipelines.pipeline import AudioPipeline


class OperatorPipeline(AudioPipeline):
    def __init__(self, operation):
        super().__init__()
        self.operation = operation
        self.data = np.array(self.operation(), copy=True)

    def c_update(self):
        self.data[...] = self.operation()
