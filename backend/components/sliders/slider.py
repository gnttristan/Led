from backend.attributes.attribute import Attribute, AttributeType


class BSlider(Attribute):
    def __init__(self, min_value, max_value, value=None, attr_type=AttributeType.NONE):
        super().__init__(min_value if value is None else value, attr_type=attr_type)
        self.min_value = min_value
        self.max_value = max_value
        self.steps = 1000

    def map_value(self, ratio):
        return self.min_value + (self.max_value - self.min_value) * ratio

    def unmap_value(self, value):
        if self.max_value == self.min_value:
            return 0
        return (value - self.min_value) / (self.max_value - self.min_value)

    def set_from_ratio(self, ratio):
        ratio = min(max(ratio, 0), 1)
        self.value = self.map_value(ratio)

    def set_from_slider(self, bSlider_value):
        self.set_from_ratio(bSlider_value / self.steps)

    def to_slider(self):
        return int(self.unmap_value(self.value) * self.steps)

    @staticmethod
    def format_value(value):
        if isinstance(value, float):
            return f"{value:.4g}"
        return str(value)
