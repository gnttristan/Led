import numpy as np

from Pipeline.pipeline import VisualPipeline
from config import FREQ_BINS


class EnergyToAlphaPipeline(VisualPipeline):
    def __init__(self, energy):
        super().__init__()
        self.energy = energy
        self.alpha = np.zeros(FREQ_BINS)

    def update(self):
        min_alpha = 0.5
        alpha = (min_alpha + (self.energy * (1 - min_alpha))) * 255
        self.alpha[:] = np.repeat(alpha, FREQ_BINS)
