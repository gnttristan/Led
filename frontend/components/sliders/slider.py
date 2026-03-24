from pyqtgraph.Qt import QtCore, QtWidgets


class FSlider(QtWidgets.QWidget):
    def __init__(self, obj):
        super().__init__()
        self.obj = obj

        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setRange(0, self.obj.steps)
        self.slider.setValue(self.obj.to_slider())
        self.value_label = QtWidgets.QLabel("")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)

        self.slider.valueChanged.connect(self.obj.set_from_slider)
        self.slider.valueChanged.connect(self._update_label)
        self._update_label()

    def _update_label(self):
        self.value_label.setText(self.obj.format_value(self.obj.value))
