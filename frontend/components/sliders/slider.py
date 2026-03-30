from pyqtgraph.Qt import QtCore, QtWidgets

from frontend.components.element.element import Element


class Slider(Element):
    def __init__(self, node, name, min_value, max_value, value=None, **kwargs):
        super().__init__(node, name, value)
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value if self.value is None else self.value
        self.steps = 1000

        if not node.render:
            return

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setFixedWidth(100)
        self.slider.setContentsMargins(0, 0, 0, 0)
        self.slider.setRange(0, self.steps)
        self.slider.setValue(self.to_slider())
        self.slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)

        self.slider.valueChanged.connect(self.set_from_slider)

        self.container_vchange_layout.addWidget(self.slider)

    def map_value(self, ratio):
        return self.min_value + (self.max_value - self.min_value) * ratio

    def unmap_value(self, value):
        if self.max_value == self.min_value:
            return 0
        return (value - self.min_value) / (self.max_value - self.min_value)

    def set_from_ratio(self, ratio):
        ratio = min(max(ratio, 0), 1)
        self.value = self.map_value(ratio)
        self.refresh_value_label()

    def set_from_slider(self, slider_value):
        self.set_from_ratio(slider_value / self.steps)

    def to_slider(self):
        return int(self.unmap_value(self.value) * self.steps)

    @staticmethod
    def format_value(value):
        if isinstance(value, float):
            return f"{value:.4g}"
        return str(value)
