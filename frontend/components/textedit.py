from pyqtgraph.Qt import QtWidgets

from frontend.components.element.element import Element


class TextEdit(Element):
    def __init__(self, node, name, value=None):
        super().__init__(node, name, value)

        if not node.render:
            return

        self.text_edit = QtWidgets.QLineEdit(str(self.value))
        self.text_edit.textEdited.connect(self.on_text_edited)
        self.container_vchange_layout.addWidget(self.text_edit)

    def on_text_edited(self, text):
        self.value = text
