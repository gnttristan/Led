import numpy as np

from backend.pipelines.pipeline import VisualPipeline
from backend.config import FREQ_BINS


class RGBAPipeline(VisualPipeline):
    def __init__(self, rgb, alpha):
        super().__init__()
        self.rgb = rgb
        self.alpha = alpha
        self.rgba = np.zeros((FREQ_BINS, 4))

    def update(self):
        rgb = self.rgb[:FREQ_BINS]

        self.rgba[:] = np.concatenate(
            (rgb, self.alpha[:, np.newaxis]), axis=1
        )
