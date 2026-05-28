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

        self.edits = []
        self._build_controls()

        self.container_vchange_layout.addWidget(self.controls_container)
        self.valueChanged.connect(self.sync_controls)
        self.sync_controls()

    @staticmethod
    def _normalize_interval(value):
        if isinstance(value, np.ndarray):
            value = value.tolist()
        if not isinstance(value, (list, tuple)) or len(value) < 2:
            raise ValueError("Interval value must be a list or tuple with at least 2 items")
        return [float(item) for item in value]

    @staticmethod
    def _format_number(value):
        return f"{float(value):.6g}"

    def _build_controls(self):
        for index, _value in enumerate(self.value):
            if index > 0:
                separator_label = QtWidgets.QLabel("-")
                separator_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                separator_label.setFixedWidth(16)
                self.controls_layout.addWidget(separator_label)

            edit = QtWidgets.QLineEdit()
            edit.setFixedSize(60, 22)
            edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            edit.editingFinished.connect(self.set_from_inputs)
            self.controls_layout.addWidget(edit)
            self.edits.append(edit)

    def set_from_inputs(self):
        try:
            values = [float(edit.text().strip()) for edit in self.edits]
        except ValueError:
            self.sync_controls()
            return
        self.value = values

    def sync_controls(self):
        values = self._normalize_interval(self.value)
        for edit, value in zip(self.edits, values):
            edit.setText(self._format_number(value))
