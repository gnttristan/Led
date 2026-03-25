from enum import Enum

class AttributeType(Enum):
    NONE = 0,
    IN = 1,
    OUT = 2,


class Attribute:
    def __init__(self, value, attr_type: AttributeType = AttributeType.NONE):
        self.value = value
        self.attr_type = attr_type
        self.value_type = type(value)
