from collections.abc import Sequence

from PyQt5 import QtCore

from frontend.components.elements.element import Element
from frontend.overrides.CComboBox import CComboBox
from frontend.overrides.CNode import CNode


class Dropbox(Element):
    def __init__(
        self,
        node: CNode,
        name: str,
        value: object = None,
        items: Sequence[str] = (),
        **kwargs: object,
    ) -> None:
        super().__init__(node, name, value, **kwargs)

        self.items = list(items)
        self.combobox = CComboBox()
        self.combobox.setFixedSize(100, 20)
        self.combobox.setContentsMargins(0, 0, 0, 0)
        self.combobox.setMinimumContentsLength(10)
        self.combobox.view().setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.combobox.addItems(self.items)

        if str(self.value) in self.items:
            self.combobox.setCurrentText(str(self.value))

        self.combobox.currentTextChanged.connect(self.on_item_changed)
        self.container_vchange_layout.addWidget(self.combobox)

    def on_item_changed(self, item: str) -> None:
        self.value = item
