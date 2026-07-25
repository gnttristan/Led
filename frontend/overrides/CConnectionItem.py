from PyQt5 import QtCore, QtGui
from pyqtgraph.flowchart.Terminal import ConnectionItem

from frontend.overrides.node_style import node_accent, tint


class CConnectionItem(ConnectionItem):
    def __init__(self, source, target=None, color=None):
        super().__init__(source, target)
        color = color or self.source_node_color()
        self.setStyle(
            color=QtGui.QColor(color),
            hoverColor=QtGui.QColor(tint(color, 0.55, "#ffffff")),
            selectedColor=QtGui.QColor("#f0d66b"),
            width=1.6,
            hoverWidth=2.2,
            selectedWidth=2.6,
        )

    def source_node_color(self):
        terminal = getattr(self.source, "term", None)
        if terminal is None:
            return node_accent()
        return node_accent(terminal.node().__class__.__module__)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape and self.isSelected():
            self.source.disconnect(self.target)
            event.accept()
            return
        super().keyPressEvent(event)
