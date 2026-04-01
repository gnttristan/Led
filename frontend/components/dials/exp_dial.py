import math

from frontend.components.dials.dial import Dial


class ExpDial(Dial):
    def map_value(self, ratio):
        return self.min_value * ((self.max_value / self.min_value) ** ratio)

    def unmap_value(self, value):
        return math.log(value / self.min_value) / math.log(self.max_value / self.min_value)
