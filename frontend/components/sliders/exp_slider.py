import math

from frontend.components.sliders.linear_slider import LinearSlider


class ExpSlider(LinearSlider):
    def map_value(self, ratio):
        return self.min_value * ((self.max_value / self.min_value) ** ratio)

    def unmap_value(self, value):
        return math.log(value / self.min_value) / math.log(self.max_value / self.min_value)
