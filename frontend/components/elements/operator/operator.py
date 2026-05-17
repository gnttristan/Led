from PyQt5 import QtCore

from frontend.components.elements.element import Element
from frontend.overrides.CComboBox import CComboBox
from frontend.overrides.CNode import CNode


class Operator(Element):
    operations = ['(', '+', '-', '*', '**', '/', ')', '<', '<=', '=>', '>']

    def __init__(self, node: CNode, name: str, value: object = None, **kwargs: object) -> None:
        super().__init__(node, name, value, **kwargs)

        self.operator_combobox = CComboBox()
        self.operator_combobox.setFixedSize(100, 20)
        self.operator_combobox.setContentsMargins(0, 0, 0, 0)
        self.operator_combobox.setMinimumContentsLength(10)
        self.operator_combobox.view().setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.operator_combobox.addItems(self.operations)

        if str(self.value) in self.operations:
            self.operator_combobox.setCurrentText(str(self.value))

        self.operator_combobox.currentTextChanged.connect(self.on_operator_changed)
        self.container_vchange_layout.addWidget(self.operator_combobox)

    def on_operator_changed(self, operator: str) -> None:
        self.value = operator
