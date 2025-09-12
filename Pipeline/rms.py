import numpy as np
from scipy.signal import hilbert, butter, lfilter

from Pipeline.pipeline import AudioPipeline
from config import SAMPLE_RATE
from energy.config import KICK_LOW_FREQT, KICK_HIGH_FREQT


class RMSPipeline(AudioPipeline):
    def __init__(self, buffer_data):
        super().__init__()
        self.buffer_data = buffer_data
        self.data = np.ones(1)

    def update(self):
        self.data[:] = np.sqrt(np.mean(self.buffer_data ** 2))
