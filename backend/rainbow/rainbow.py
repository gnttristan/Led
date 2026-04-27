import colorsys

import numpy as np

from backend.updatable.updatable import VisualUpdatable
from config import FREQ_BINS
from backend.rainbow.config import RAINBOW_INV_FRACTION


class Rainbow(VisualUpdatable):
    def __init__(
        self,
        inv_fraction=RAINBOW_INV_FRACTION,
        n_points=FREQ_BINS,
        color_in=(255, 0, 0),
        color_out=(255, 0, 0),
        cycle=1,
    ):
        super().__init__()
        self.inv_fraction = inv_fraction
        self.n_points = n_points
        self._color_in = color_in
        self._color_out = color_out
        self._cycle = cycle
        self.data = self.get_rainbow_rbg(
            self.n_points,
            self._color_in,
            self._color_out,
            self._cycle,
        )

    def get_rainbow_rbg(
        self,
        n_points=FREQ_BINS,
        color_in=(255, 0, 0),
        color_out=(255, 0, 0),
        cycle=1,
    ):
        def to_hsv(color):
            rgb = np.asarray(color, dtype=float) / 255.0
            return np.array(colorsys.rgb_to_hsv(*rgb))

        hsv_in = to_hsv(color_in)
        hsv_out = to_hsv(color_out)
        offsets = np.linspace(0, 1, n_points, endpoint=True)

        hue = (hsv_in[0] + offsets * ((hsv_out[0] - hsv_in[0]) + cycle)) % 1.0
        saturation = hsv_in[1] + (hsv_out[1] - hsv_in[1]) * offsets
        value = hsv_in[2] + (hsv_out[2] - hsv_in[2]) * offsets

        hsv = np.stack((hue, saturation, value), axis=1)
        rgb = np.array([colorsys.hsv_to_rgb(*point) for point in hsv]) * 255
        return np.clip(np.rint(rgb), 0, 255).astype(int)

    def c_update(self):
        pass
