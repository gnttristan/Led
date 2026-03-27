from pyqtgraph.Qt import QtCore, QtWidgets


class Slider(QtWidgets.QWidget):
    def __init__(self, min_value, max_value, value=None, **kwargs):
        super().__init__()
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value if value is None else value
        self.steps = 1000

        self.value_label = QtWidgets.QLabel("")
        self.value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("background: transparent;")

        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setContentsMargins(0, 0, 0, 0)
        self.slider.setRange(0, self.steps)
        self.slider.setValue(self.to_slider())
        self.slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.value_label)
        layout.addWidget(self.slider)

        self.slider.valueChanged.connect(self.set_from_slider)
        self.slider.valueChanged.connect(self._update_label)
        self._update_label()

    def map_value(self, ratio):
        return self.min_value + (self.max_value - self.min_value) * ratio

    def unmap_value(self, value):
        if self.max_value == self.min_value:
            return 0
        return (value - self.min_value) / (self.max_value - self.min_value)

    def set_from_ratio(self, ratio):
        ratio = min(max(ratio, 0), 1)
        self.value = self.map_value(ratio)

    def set_from_slider(self, slider_value):
        self.set_from_ratio(slider_value / self.steps)

    def to_slider(self):
        return int(self.unmap_value(self.value) * self.steps)

    @staticmethod
    def format_value(value):
        if isinstance(value, float):
            return f"{value:.4g}"
        return str(value)

    def _update_label(self):
        self.value_label.setText(self.format_value(self.value))
