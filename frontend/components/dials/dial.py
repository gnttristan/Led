from pyqtgraph.Qt import QtCore, QtWidgets

from frontend.components.element.element import Element


class Dial(Element):
    def __init__(self, node, name, min_value, max_value, value=None, **kwargs):
        super().__init__(node, name, value)
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value if self.value is None else self.value
        self.steps = 1000

        if not node.render:
            return

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.controls_container = QtWidgets.QWidget()
        self.controls_layout = QtWidgets.QHBoxLayout(self.controls_container)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.setSpacing(4)

        self.dial = QtWidgets.QDial()
        self.dial.setFixedSize(40, 40)
        self.dial.setContentsMargins(0, 0, 0, 0)
        self.dial.setRange(0, self.steps)
        self.dial.setValue(self.to_dial())
        self.dial.setNotchesVisible(True)

        self.dial.valueChanged.connect(self.set_from_dial)
        self.controls_layout.addWidget(self.dial)

        self.value_edit = QtWidgets.QLineEdit()
        self.value_edit.setFixedSize(40, 40)
        self.value_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.value_edit.editingFinished.connect(self.set_from_line_edit)
        self.controls_layout.addWidget(self.value_edit)

        self.container_vchange_layout.addWidget(self.controls_container)
        self.sync_controls()

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
        self.sync_controls()

    def set_from_dial(self, dial_value):
        self.set_from_ratio(dial_value / self.steps)

    def set_from_line_edit(self):
        text = self.value_edit.text().strip()
        try:
            typed_value = float(text)
        except ValueError:
            self.sync_controls()
            return

        self.set_from_ratio(self.unmap_value(typed_value))

    def sync_controls(self):
        if hasattr(self, "dial"):
            dial_value = self.to_dial()
            if self.dial.value() != dial_value:
                self.dial.blockSignals(True)
                self.dial.setValue(dial_value)
                self.dial.blockSignals(False)
        if hasattr(self, "value_edit"):
            formatted_value = self.format_value(self.value)
            if self.value_edit.text() != formatted_value:
                self.value_edit.blockSignals(True)
                self.value_edit.setText(formatted_value)
                self.value_edit.blockSignals(False)

    def to_dial(self):
        return int(self.unmap_value(self.value) * self.steps)

    @staticmethod
    def format_value(value):
        if isinstance(value, float):
            return f"{value:.4g}"
        return str(value)
