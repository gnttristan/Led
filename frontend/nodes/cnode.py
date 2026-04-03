from types import MethodType

from PyQt5 import QtGui, QtWidgets
from pyqtgraph.Qt import QtCore
from pyqtgraph.flowchart import Node

from frontend.overrides.CTerminal import CTerminal


class CNode(Node):
    sig_initiated = QtCore.Signal()
    INNER_MARGIN = 10
    TERMINAL_WIDTH = 40
    TITLE_OFFSET = 24

    def __init__(self, node_name, terminals, render=True):
        self.node_name = node_name
        self.render = render
        self.elements = []
        self.pending_terminals = dict(terminals)
        self._elements_proxy = None
        self._elements_container = None
        self.is_child = False
        self.is_initiated = False

        if not render:
            return

        super().__init__(node_name)
        QtCore.QTimer.singleShot(0, self.init_terminals)
        QtCore.QTimer.singleShot(0, self.init_elements)

    def init_terminals(self):
        for name, opts in self.pending_terminals.items():
            self.addTerminal(name, **opts)

    def init_elements(self):
        if self._elements_proxy is not None:
            return

        item = super().graphicsItem()
        container = QtWidgets.QWidget()
        container.setStyleSheet(f"background-color: {item.brush.color().name()};")
        container.setStyleSheet("border: 1px solid #666;")
        self._elements_container = container

        elements_vbox = QtWidgets.QVBoxLayout(container)
        elements_vbox.setContentsMargins(0, 0, 0, 0)
        elements_vbox.setSpacing(0)

        for element in self.elements:
            elements_vbox.addWidget(element)

        self._elements_proxy = QtWidgets.QGraphicsProxyWidget(item)
        self._elements_proxy.setWidget(container)
        self._elements_proxy.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, False)
        self._elements_proxy.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsPanel, True)
        self._elements_proxy.setZValue(1)
        self._elements_proxy.setPos(self.INNER_MARGIN, self.TITLE_OFFSET)

        item.updateTerminals()
        self.refresh_terminal_positions()

    def refresh_parents_sizes(self):
        if not self.render or self._elements_proxy is None or self._elements_container is None:
            return

        item = super().graphicsItem()
        self._elements_container.adjustSize()
        content_size = self._elements_container.sizeHint()
        self._elements_proxy.resize(content_size.width(), content_size.height())
        item.bounds.setWidth(content_size.width() + self.INNER_MARGIN * 2)
        item.bounds.setHeight(self.TITLE_OFFSET + content_size.height() + self.INNER_MARGIN)
        item.update()

    def refresh_terminal_positions(self):
        if not self.render or self._elements_proxy is None or self._elements_container is None:
            return

        self.refresh_parents_sizes()

        for element in self.elements:
            if hasattr(element, "attach_terminal"):
                element.attach_terminal(self.TITLE_OFFSET, self.INNER_MARGIN)

    def addTerminal(self, name, **opts):
        term = super().addTerminal(name, **opts)
        term.connectTo = MethodType(CTerminal.connectTo, term)
        return term

    def c_update(self, **kwargs):
        return {}
