import math

from backend.components.sliders.slider import BSlider


class BExpSlider(BSlider):
    def map_value(self, ratio):
        return self.min_value * ((self.max_value / self.min_value) ** ratio)

    def unmap_value(self, value):
        return math.log(value / self.min_value) / math.log(self.max_value / self.min_value)
