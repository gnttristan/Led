from PyQt5 import QtWidgets

from frontend.components.elements.element import Element
from frontend.overrides.CNode import CNode


class TextEdit(Element):
    def __init__(self, node: CNode, name: str, value: object = None, **kwargs: object) -> None:
        super().__init__(node, name, value, **kwargs)

        self.text_edit = QtWidgets.QLineEdit(str(self.value))
        self.text_edit.setFixedWidth(100)
        self.text_edit.textEdited.connect(self.on_text_edited)
        self.container_vchange_layout.addWidget(self.text_edit)
        self.valueChanged.connect(self.sync_controls)
        self.sync_controls()

    def on_text_edited(self, text):
        self.value = text

    def sync_controls(self):
        text = str(self.value)
        if self.text_edit.text() == text:
            return
        self.text_edit.blockSignals(True)
        self.text_edit.setText(text)
        self.text_edit.blockSignals(False)
