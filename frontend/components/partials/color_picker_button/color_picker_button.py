import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from frontend.overrides.node_style import color_button_stylesheet


class ColorPickerButton(QtWidgets.QPushButton):
    valueChanged = QtCore.pyqtSignal(object)

    def __init__(self, name: str, value=(255, 0, 0), parent=None) -> None:
        super().__init__(parent)
        self.name = name
        self._value = self._normalize_color(value)
        self.setFixedSize(74, 24)
        self.clicked.connect(self.open_color_dialog)
        self.sync_controls()

    @staticmethod
    def _normalize_color(color_value) -> tuple:
        if isinstance(color_value, str):
            text = color_value.strip().lstrip("#")
            if len(text) != 6:
                raise ValueError("Color string must be in #RRGGBB format")
            return tuple(int(text[i:i + 2], 16) for i in range(0, 6, 2))

        if isinstance(color_value, np.ndarray):
            color_value = color_value.tolist()

        if isinstance(color_value, (tuple, list)) and len(color_value) == 3:
            return tuple(int(np.clip(round(float(channel)), 0, 255)) for channel in color_value)

        raise ValueError("Color value must be an RGB tuple, list, or #RRGGBB string")

    @staticmethod
    def _color_to_hex(color: tuple[int, int, int]) -> str:
        return "#{:02X}{:02X}{:02X}".format(*color)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value) -> None:
        self.set_value(value)

    def set_value(self, value, emit: bool = True) -> None:
        self._value = self._normalize_color(value)
        self.sync_controls()
        if emit:
            self.valueChanged.emit(self._value)

    def _to_qcolor(self) -> QtGui.QColor:
        return QtGui.QColor(*self._value)

    def open_color_dialog(self) -> None:
        color = QtWidgets.QColorDialog.getColor(self._to_qcolor(), self, f"Select {self.name} color")
        if color.isValid():
            self.value = (color.red(), color.green(), color.blue())

    def sync_controls(self) -> None:
        hex_value = self._color_to_hex(self._value)
        self.blockSignals(True)
        self.setText(hex_value)
        self.setStyleSheet(color_button_stylesheet(hex_value))
        self.blockSignals(False)
