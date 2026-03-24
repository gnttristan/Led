import numpy as np

from backend.rainbow.config import RAINBOW_INV_FRACTION, ROLL_SPEED
from backend.rainbow.rainbow import Rainbow


class GradiantRainbow(Rainbow):
    def __init__(
            self,
            roll_speed=ROLL_SPEED,
            inv_fraction=RAINBOW_INV_FRACTION
    ):
        super().__init__(inv_fraction)
        self.roll_speed = roll_speed

    def update(self):
        super().update()
        self.roll_rainbow()

    def roll_rainbow(self):
        self.data[:] = np.roll(self.data, self.roll_speed, axis=0)



