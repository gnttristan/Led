import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from frontend.components.elements.element import Element
from frontend.overrides.CNode import CNode
from frontend.overrides.node_style import color_button_stylesheet


class ColorPicker(Element):
    def __init__(
        self,
        node: CNode,
        name: str,
        value: object = (255, 0, 0),
        **kwargs: object,
    ) -> None:
        super().__init__(node, name, value, **kwargs)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.controls_container = QtWidgets.QWidget()
        self.controls_layout = QtWidgets.QHBoxLayout(self.controls_container)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.setSpacing(4)

        self.color_button = QtWidgets.QPushButton()
        self.color_button.setFixedSize(74, 24)
        self.color_button.clicked.connect(self.open_color_dialog)
        self.controls_layout.addWidget(self.color_button)

        self.container_vchange_layout.addWidget(self.controls_container)
        self.valueChanged.connect(self.sync_controls)
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

    def _to_qcolor(self) -> QtGui.QColor:
        return QtGui.QColor(*self._normalize_color(self.value))

    def open_color_dialog(self) -> None:
        color = QtWidgets.QColorDialog.getColor(self._to_qcolor(), self, f"Select {self.name} color")
        if color.isValid():
            self.value = (color.red(), color.green(), color.blue())

    def sync_controls(self) -> None:
        color = self._normalize_color(self.value)
        hex_value = self._color_to_hex(color)

        self.color_button.blockSignals(True)
        self.color_button.setText(hex_value)
        self.color_button.setStyleSheet(color_button_stylesheet(hex_value))
        self.color_button.blockSignals(False)
