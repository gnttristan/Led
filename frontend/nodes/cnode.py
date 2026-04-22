import inspect
from typing import Mapping

from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
from PyQt5 import sip
from pyqtgraph.flowchart import Node

from frontend.overrides.CTerminal import CTerminal


class CNode(Node):
    sig_initiated = QtCore.pyqtSignal()
    INNER_MARGIN = 10
    TERMINAL_WIDTH = 40
    TITLE_OFFSET = 24

    def __init__(
        self,
        node_name: str,
        terminals: Mapping[str, Mapping[str, object]],
        render: bool = True,
        is_child: bool = False,
    ) -> None:
        self.node_name = node_name
        self.render = render
        self.elements = []
        self.pending_terminals = dict(terminals)
        self._elements_proxy = None
        self._elements_container = None
        self.is_child = is_child
        self.is_initiated = False

        super().__init__(node_name)

        if not render:
            return

        QtCore.QTimer.singleShot(0, self.init_all)

    def init_all(self):
        self.init_terminals()
        self.init_elements()

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

        for element in self._live_elements():
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
        item = super().graphicsItem()
        content_size = self._elements_container.size()
        self._elements_proxy.resize(content_size.width(), content_size.height())
        item.bounds.setWidth(content_size.width() + self.INNER_MARGIN * 2)
        item.bounds.setHeight(self.TITLE_OFFSET + content_size.height() + self.INNER_MARGIN)
        item.update()

    def refresh_terminal_positions(self):
        self.refresh_parents_sizes()

        for element in self._live_elements():
            if hasattr(element, "attach_terminal"):
                element.attach_terminal(self.TITLE_OFFSET, self.INNER_MARGIN)

    def _live_elements(self):
        live_elements = []
        for element in self.elements:
            if isinstance(element, QtWidgets.QWidget) and not sip.isdeleted(element):
                live_elements.append(element)
        self.elements = live_elements
        return live_elements

    def addTerminal(self, name, **opts):
        name = self.nextTerminalName(name)
        term = CTerminal(self, name, **opts)
        self.terminals[name] = term
        if term.isInput():
            self._inputs[name] = term
        elif term.isOutput():
            self._outputs[name] = term
        self.graphicsItem().updateTerminals()
        self.sigTerminalAdded.emit(self, term)
        return term

    def connected(self, localTerm, remoteTerm):
        if not localTerm.isInput() or not remoteTerm.isOutput():
            return

        local_element = getattr(self, localTerm.name(), None)
        remote_element = getattr(remoteTerm.node(), remoteTerm.name(), None)

        if local_element is None or remote_element is None:
            return

        if not hasattr(local_element, "value") or not hasattr(remote_element, "value"):
            return

        # Keep input elements synced to their connected output terminal value.
        local_element.value = lambda: remote_element.value

    def disconnected(self, localTerm, remoteTerm):
        if not localTerm.isInput() or not remoteTerm.isOutput():
            return

        local_element = getattr(self, localTerm.name(), None)
        if local_element is None or not hasattr(local_element, "value"):
            return

        init_signature = inspect.signature(type(self).__init__)
        parameter = init_signature.parameters.get(localTerm.name())
        if parameter is None or parameter.default is inspect._empty:
            return

        local_element.value = parameter.default

    def get_flowchart_visible_nodes(self):
        return self.graphicsItem().getViewBox().widget.chart.visible_nodes

    def c_update(self, **kwargs):
        return {}
