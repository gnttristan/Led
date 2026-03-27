import numpy as np

from backend.pipelines.pipeline import VisualPipeline
from backend.config import FREQ_BINS

POWER_LOG = 1

class RGBPPipeline(VisualPipeline):
    def __init__(self, rgb, alpha, power_log=POWER_LOG):
        super().__init__()
        self.rgb = rgb
        self.alpha = alpha
        self.output_rgb = np.zeros((FREQ_BINS, 3), dtype=np.float32)
        self.power_log = power_log

    def c_update(self):
        rgb = self.rgb[:FREQ_BINS]

        self.output_rgb[:] = (
                rgb *
                (np.power((self.alpha / 255), self.power_log)[:, None])
        )