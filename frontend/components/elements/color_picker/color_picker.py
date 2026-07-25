from PyQt5 import QtCore, QtWidgets

from frontend.components.elements.element import Element
from frontend.overrides.CNode import CNode
from frontend.components.partials.color_picker_button import ColorPickerButton


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

        self.color_button = ColorPickerButton(self.name, self.value, self)
        self.color_button.valueChanged.connect(self._set_value_from_button)
        self.valueChanged.connect(lambda value: self.color_button.set_value(value, emit=False))
        self.controls_layout.addWidget(self.color_button)

        self.container_vchange_layout.addWidget(self.controls_container)

    def _set_value_from_button(self, value) -> None:
        self.value = value
