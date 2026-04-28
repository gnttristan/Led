import math

from frontend.components.elements.dials.dial import Dial


class ExpDial(Dial):
    def map_value(self, ratio):
        return self.min_value * ((self.max_value / self.min_value) ** ratio)

    def unmap_value(self, value):
        self.min_value = 1e-3 if self.min_value == 0 else self.min_value
        if value / self.min_value == 0:
            return 0
        return math.log(value / self.min_value) / math.log(self.max_value / self.min_value)
