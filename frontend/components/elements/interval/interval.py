import numpy as np
from PyQt5 import QtCore, QtWidgets

from frontend.components.elements.element import Element
from frontend.overrides.CNode import CNode


class Interval(Element):
    def __init__(
        self,
        node: CNode,
        name: str,
        value: object = (0.0, 1.0),
        **kwargs: object,
    ) -> None:
        super().__init__(node, name, value, **kwargs)
        self.value = self._normalize_interval(self.value)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.controls_container = QtWidgets.QWidget()
        self.controls_layout = QtWidgets.QHBoxLayout(self.controls_container)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.setSpacing(4)

        self.min_edit = QtWidgets.QLineEdit()
        self.min_edit.setFixedSize(60, 22)
        self.min_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.min_edit.editingFinished.connect(self.set_from_inputs)
        self.controls_layout.addWidget(self.min_edit)

        self.separator_label = QtWidgets.QLabel("-")
        self.separator_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.separator_label.setFixedWidth(16)
        self.controls_layout.addWidget(self.separator_label)

        self.max_edit = QtWidgets.QLineEdit()
        self.max_edit.setFixedSize(60, 22)
        self.max_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.max_edit.editingFinished.connect(self.set_from_inputs)
        self.controls_layout.addWidget(self.max_edit)

        self.container_vchange_layout.addWidget(self.controls_container)
        self.valueChanged.connect(self.sync_controls)
        self.sync_controls()

    @staticmethod
    def _normalize_interval(value):
        if isinstance(value, np.ndarray):
            value = value.tolist()
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("Interval value must be a 2-item list or tuple")
        return [float(value[0]), float(value[1])]

    @staticmethod
    def _format_number(value):
        return f"{float(value):.6g}"

    def set_from_inputs(self):
        try:
            min_value = float(self.min_edit.text().strip())
            max_value = float(self.max_edit.text().strip())
        except ValueError:
            self.sync_controls()
            return
        self.value = [min_value, max_value]

    def sync_controls(self):
        min_value, max_value = self._normalize_interval(self.value)
        self.min_edit.setText(self._format_number(min_value))
        self.max_edit.setText(self._format_number(max_value))
