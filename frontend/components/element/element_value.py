class ElementValue:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        value = self._value
        while True:
            if isinstance(value, ElementValue):
                value = value.value
                continue
            if callable(value):
                value = value()
                continue
            break
        return value

    @value.setter
    def value(self, value):
        if callable(value):
            self._value = value
            return
        while isinstance(value, ElementValue):
            value = value.value
        self._value = value
