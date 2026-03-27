from types import MethodType

from pyqtgraph.Qt import QtCore
from pyqtgraph.flowchart import Node

from frontend.overrides.CTerminal import CTerminal


class CNode(Node):
    def __init__(self, node_name, terminals):
        super().__init__(node_name)
        self._pending_terminals = dict(terminals)
        QtCore.QTimer.singleShot(0, self._init_terminals)

    def _init_terminals(self):
        for name, opts in self._pending_terminals.items():
            self.addTerminal(name, **opts)

    def addTerminal(self, name, **opts):
        term = super().addTerminal(name, **opts)
        term.connectTo = MethodType(CTerminal.connectTo, term)
        return term

    def c_update(self, **kwargs):
        return {}
