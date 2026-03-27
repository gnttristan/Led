import numpy as np

from backend.pipelines.pipeline import AudioPipeline


class RMSPipeline(AudioPipeline):
    def __init__(self, buffer_data):
        super().__init__()
        self.buffer_data = buffer_data
        self.data = np.ones(1)

    def c_update(self):
        self.data[:] = np.sqrt(np.mean(self.buffer_data ** 2))
