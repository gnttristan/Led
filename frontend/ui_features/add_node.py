from PyQt5 import QtCore, QtWidgets

from frontend.registry.registry import nodes


class AddNodeFeature(QtCore.QObject):
    def __init__(self, flowchart):
        super().__init__(flowchart.widget())
        self.flowchart = flowchart
        self.node_classes = sorted(nodes, key=lambda node: node.nodeName)

        self.popup = QtWidgets.QFrame(flowchart.widget())
        self.popup.setWindowFlags(QtCore.Qt.WindowType.Popup)
        self.popup.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        layout = QtWidgets.QVBoxLayout(self.popup)
        layout.setContentsMargins(6, 6, 6, 6)

        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search nodes")
        self.search.textChanged.connect(self._refresh)
        self.search.returnPressed.connect(self._add_selected)
        layout.addWidget(self.search)

        self.results = QtWidgets.QListWidget()
        self.results.itemDoubleClicked.connect(lambda _: self._add_selected())
        layout.addWidget(self.results)
        self.popup.resize(320, 360)
        self.popup.hide()

        QtWidgets.QApplication.instance().installEventFilter(self)
        self._refresh("")

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.Type.KeyPress:
            command = QtCore.Qt.KeyboardModifier.ControlModifier | QtCore.Qt.KeyboardModifier.MetaModifier
            if event.key() == QtCore.Qt.Key.Key_A and event.modifiers() & command:
                self._show()
                return True
            if self.popup.isVisible() and event.key() == QtCore.Qt.Key.Key_Escape:
                self.popup.hide()
                return True
            if self.popup.isVisible() and event.key() in (QtCore.Qt.Key.Key_Up, QtCore.Qt.Key.Key_Down):
                step = -1 if event.key() == QtCore.Qt.Key.Key_Up else 1
                row = (self.results.currentRow() + step) % self.results.count()
                self.results.setCurrentRow(row)
                return True
        return False

    def _show(self):
        self.popup.move(
            (self.flowchart.widget().width() - self.popup.width()) // 2,
            20,
        )
        self.popup.show()
        self.search.clear()
        self.search.setFocus()

    def _refresh(self, query):
        query = query.lower()
        self.results.clear()
        for node in self.node_classes:
            if query in node.nodeName.lower():
                item = QtWidgets.QListWidgetItem(node.nodeName)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, node)
                self.results.addItem(item)
        if self.results.count():
            self.results.setCurrentRow(0)

    def _add_selected(self):
        item = self.results.currentItem()
        if item is None:
            return
        self.popup.hide()
        self.flowchart.createNode(item.text())
