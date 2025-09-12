import numpy as np

from Updatable.updatable import AudioUpdatable
from config import FREQ_BINS

class ExpandedAmplitudes(AudioUpdatable):
    def __init__(self, amplitudes, size=FREQ_BINS):
        super().__init__()
        self.amplitudes = amplitudes
        self.size = size
        self.groups_indexes = np.cumsum(np.repeat(size / amplitudes.shape[0], amplitudes.shape[0], )).astype(int)
        self.diff_indexes = np.hstack((self.groups_indexes[0], np.diff(self.groups_indexes)))
        self.data = np.zeros(size)

    def update(self):
        super().update()
        self.data[:] = np.repeat(self.amplitudes, self.diff_indexes)


