import math

from frontend.components.sliders.slider import Slider


class LogSlider(Slider):
    def map_value(self, ratio):
        min_log = math.log(self.min_value)
        max_log = math.log(self.max_value)
        return math.exp(min_log + (max_log - min_log) * ratio)

    def unmap_value(self, value):
        min_log = math.log(self.min_value)
        max_log = math.log(self.max_value)
        return (math.log(value) - min_log) / (max_log - min_log)
