import inspect
from typing import Mapping

import numpy as np
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
    _SERDE_TAG = "__cnode_serde__"

    def __init__(
        self,
        node_name: str,
        terminals: Mapping[str, Mapping[str, object]],
        render: bool = True,
        parent: "CNode | None" = None,
        alias: str | None = None,
    ) -> None:
        self.node_name = node_name
        self.alias = alias or node_name
        self.render = render
        self.elements = []
        self.pending_terminals = dict(terminals)
        self._elements_proxy = None
        self._elements_container = None
        self.parent = parent
        self.is_initiated = False

        super().__init__(self.alias)

        if not render:
            return

        QtCore.QTimer.singleShot(0, self.init_all)

    def init_all(self):
        self.init_terminals()
        self.init_elements()
        self.connect_position_refresh()

    def connect_position_refresh(self):
        if getattr(self, "_position_refresh_connected", False):
            return
        item = self.graphicsItem()
        item.xChanged.connect(self.refresh_embedded_child_terminal_positions)
        item.yChanged.connect(self.refresh_embedded_child_terminal_positions)
        self._position_refresh_connected = True

    def refresh_embedded_child_terminal_positions(self):
        for element in self._live_elements():
            value = getattr(element, "value", None)
            child_nodes = value if isinstance(value, list) else [value]
            for child_node in child_nodes:
                if isinstance(child_node, CNode) and child_node.parent is self:
                    child_node.refresh_terminal_positions()

    def saveState(self):
        state = super().saveState()
        init_signature = inspect.signature(type(self).__init__)
        ctor_kwargs = {}
        init_refs = {}

        for parameter_name, parameter in init_signature.parameters.items():
            if parameter_name in {"self", "render", "alias"}:
                continue

            terminal = self.terminals.get(parameter_name.lower())
            remote_terminal = (
                next(iter(terminal.connections().keys()), None)
                if terminal is not None and terminal.isInput()
                else None
            )

            if remote_terminal is not None and remote_terminal.isOutput():
                init_refs[parameter_name] = {
                    "__element_ref__": {
                        "node_name": remote_terminal.node().name(),
                        "element_name": remote_terminal.name(),
                    }
                }
                remote_owner = getattr(remote_terminal.node(), "obj", remote_terminal.node())
                if hasattr(remote_owner, remote_terminal.name()):
                    remote_element = getattr(remote_owner, remote_terminal.name())
                    if hasattr(remote_element, "value"):
                        raw_value = remote_element.value
                    else:
                        raw_value = remote_element
                else:
                    raw_value = None
            elif hasattr(self, parameter_name):
                raw_value = getattr(self, parameter_name)
                if hasattr(raw_value, "value"):
                    raw_value = raw_value.value
            elif parameter.default is not inspect._empty:
                raw_value = parameter.default
            else:
                raw_value = None

            serialized_value = self.serialize_state_value(raw_value)
            if serialized_value is not None:
                ctor_kwargs[parameter_name] = serialized_value

        if ctor_kwargs:
            state["ctor_kwargs"] = ctor_kwargs
        if init_refs:
            state["init_refs"] = init_refs

        return state

    @classmethod
    def serialize_state_value(cls, value):
        if isinstance(value, np.ndarray):
            return {
                cls._SERDE_TAG: "ndarray",
                "dtype": str(value.dtype),
                "value": value.tolist(),
            }
        if isinstance(value, np.generic):
            return {
                cls._SERDE_TAG: "npscalar",
                "dtype": str(value.dtype),
                "value": value.item(),
            }
        if isinstance(value, tuple):
            serialized = []
            for item in value:
                item_value = cls.serialize_state_value(item)
                if item_value is None:
                    return None
                serialized.append(item_value)
            return {
                cls._SERDE_TAG: "tuple",
                "value": serialized,
            }
        if isinstance(value, list):
            serialized = []
            for item in value:
                item_value = cls.serialize_state_value(item)
                if item_value is None:
                    return None
                serialized.append(item_value)
            return serialized
        if isinstance(value, dict):
            serialized_dict = {}
            for key, item in value.items():
                item_value = cls.serialize_state_value(item)
                if item_value is None:
                    return None
                serialized_dict[key] = item_value
            return serialized_dict
        if callable(value):
            return None
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        return None

    @classmethod
    def deserialize_state_value(cls, value):
        if isinstance(value, dict):
            serde_type = value.get(cls._SERDE_TAG)
            if serde_type == "ndarray":
                return np.array(value["value"], dtype=np.dtype(value["dtype"]))
            if serde_type == "npscalar":
                return np.dtype(value["dtype"]).type(value["value"])
            if serde_type == "tuple":
                return tuple(cls.deserialize_state_value(item) for item in value["value"])
            return {key: cls.deserialize_state_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls.deserialize_state_value(item) for item in value]
        return value

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
        self._elements_proxy.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsPanel, False)
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
        if self.parent is not None:
            return self.parent.get_flowchart_visible_nodes()
        return self.graphicsItem().getViewBox()

    def c_update(self, **kwargs):
        return {}
