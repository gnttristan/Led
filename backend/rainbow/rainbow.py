import numpy as np

from backend.updatable.updatable import VisualUpdatable
from config import FREQ_BINS
from backend.rainbow.config import RAINBOW_INV_FRACTION


class Rainbow(VisualUpdatable):
    def __init__(self, inv_fraction=RAINBOW_INV_FRACTION):
        super().__init__()
        self.inv_fraction = inv_fraction
        self.data = self.get_rainbow_rbg()

    def get_rainbow_rbg(self):
        def get_curve(offset):
            return np.clip(510 - np.abs(np.maximum(
                offset - offset_rgb_per_color,
                - offset + (offset_rgb_per_color - 1530)
            )), 0, 255)

        rgb_flattened_values = 255 * 3 * 2
        offset_rgb_per_color = np.arange(
            0,
            rgb_flattened_values,
            (rgb_flattened_values / self.inv_fraction) / FREQ_BINS
        )

        tr, tg, tb = tuple(-255 + (510 * i) for i in range(3))
        r, g, b = get_curve(tr), get_curve(tg), get_curve(tb)
        return np.stack((r, g, b), axis=1)

    def c_update(self):
        pass