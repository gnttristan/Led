import inspect
import math
from typing import Iterable, Mapping, Any

import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5 import sip
from pyqtgraph.flowchart import Node

from frontend.overrides.CTerminal import CTerminal


class CNode(Node):
    sig_initiated = QtCore.pyqtSignal()
    INNER_MARGIN = 10
    TERMINAL_WIDTH = 40
    TITLE_OFFSET = 24
    _SERDE_TAG = "__cnode_serde__"
    _STATE_IGNORED_PARAMS = {"self", "render", "alias"}

    def __init__(
        self,
        node_name: str,
        terminals: Mapping[str, Mapping[str, object]],
        render: bool = True,
        parent: Any = None,
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
        for child_node in self.child_nodes():
            child_node.refresh_terminal_positions()

    @property
    def is_embedded(self):
        return isinstance(self.parent, CNode)

    def saveState(self):
        state = super().saveState()
        ctor_kwargs = {}
        init_refs = {}

        for parameter_name, parameter in self._init_parameters().items():
            if parameter_name in self._STATE_IGNORED_PARAMS:
                continue

            raw_value, ref = self._state_parameter_value(parameter_name, parameter)
            if ref is not None:
                init_refs[parameter_name] = ref

            serialized_value = self.serialize_state_value(raw_value)
            if serialized_value is not None:
                ctor_kwargs[parameter_name] = serialized_value

        if ctor_kwargs:
            state["ctor_kwargs"] = ctor_kwargs
        if init_refs:
            state["init_refs"] = init_refs

        return state

    @classmethod
    def _init_parameters(cls):
        return inspect.signature(cls.__init__).parameters

    def _state_parameter_value(self, parameter_name, parameter):
        remote_terminal = self._connected_output_terminal(parameter_name)
        if remote_terminal is not None:
            return self._remote_terminal_value(remote_terminal), self._element_ref(remote_terminal)

        if hasattr(self, parameter_name):
            return self._element_value(getattr(self, parameter_name)), None

        return (parameter.default, None) if parameter.default is not inspect._empty else (None, None)

    def _connected_output_terminal(self, parameter_name):
        terminal = self.terminals.get(parameter_name.lower())
        if terminal is None or not terminal.isInput():
            return None

        remote_terminal = next(iter(terminal.connections()), None)
        return remote_terminal if remote_terminal is not None and remote_terminal.isOutput() else None

    @staticmethod
    def _element_ref(terminal):
        return {
            "__element_ref__": {
                "node_name": terminal.node().name(),
                "element_name": terminal.name(),
            }
        }

    @classmethod
    def _remote_terminal_value(cls, terminal):
        owner = getattr(terminal.node(), "obj", terminal.node())
        element_name = owner.terminal_element_name(terminal.name())
        if not hasattr(owner, element_name):
            return None
        return cls._element_value(getattr(owner, element_name))

    @staticmethod
    def _element_value(value):
        return value.value if hasattr(value, "value") else value

    @classmethod
    def serialize_state_value(cls, value):
        if isinstance(value, np.ndarray):
            return cls._serde("ndarray", dtype=str(value.dtype), value=value.tolist())
        if isinstance(value, np.generic):
            return cls._serde("npscalar", dtype=str(value.dtype), value=value.item())
        if isinstance(value, tuple):
            serialized = cls._serialize_sequence(value)
            return None if serialized is None else cls._serde("tuple", value=serialized)
        if isinstance(value, list):
            return cls._serialize_sequence(value)
        if isinstance(value, dict):
            return cls._serialize_mapping(value)
        if callable(value):
            return None
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        return None

    @classmethod
    def _serde(cls, serde_type, **payload):
        return {cls._SERDE_TAG: serde_type, **payload}

    @classmethod
    def _serialize_sequence(cls, values):
        serialized = [cls.serialize_state_value(item) for item in values]
        return serialized if all(item is not None for item in serialized) else None

    @classmethod
    def _serialize_mapping(cls, values):
        serialized = {key: cls.serialize_state_value(item) for key, item in values.items()}
        return serialized if all(item is not None for item in serialized.values()) else None

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
            if name not in self.terminals:
                self.addTerminal(name, **opts)

    def init_elements(self):
        if self._elements_proxy is not None:
            return

        item = super().graphicsItem()
        container = QtWidgets.QWidget()
        container.setStyleSheet("border: 1px solid #666;")
        self._elements_container = container

        elements_vbox = QtWidgets.QVBoxLayout(container)
        elements_vbox.setContentsMargins(0, 0, 0, 0)
        elements_vbox.setSpacing(0)

        for element in self._live_elements():
            elements_vbox.addWidget(element)

        self._elements_proxy = QtWidgets.QGraphicsProxyWidget(item)
        self._elements_proxy.setWidget(container)
        self._elements_proxy.setZValue(1)
        self._elements_proxy.setPos(self.INNER_MARGIN, self.TITLE_OFFSET)

        item.updateTerminals()
        self.refresh_terminal_positions()
        QtCore.QTimer.singleShot(0, self.refresh_terminal_positions)

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
        for child_node in self.child_nodes():
            child_node.refresh_terminal_positions()

    def _live_elements(self):
        live_elements = [
            element
            for element in self.elements
            if isinstance(element, QtWidgets.QWidget) and not sip.isdeleted(element)
        ]
        self.elements = live_elements
        return live_elements

    def child_nodes(self) -> Iterable["CNode"]:
        yield from self._child_nodes(set())

    def _child_nodes(self, seen):
        for element in self._live_elements():
            for child_node in self._iter_child_values(getattr(element, "value", None)):
                if child_node.parent is not self or id(child_node) in seen:
                    continue
                seen.add(id(child_node))
                yield child_node
                yield from child_node._child_nodes(seen)

    @classmethod
    def _iter_child_values(cls, value):
        if isinstance(value, CNode):
            yield value
        if isinstance(value, list):
            for item in value:
                yield from cls._iter_child_values(item)

    def embed_in(self, parent_node, placeholder):
        self.parent = parent_node
        if self._elements_proxy is None:
            self.init_all()

        item = self.graphicsItem()
        parent_item = parent_node.graphicsItem()
        if item.parentItem() is not parent_item:
            item.setParentItem(parent_item)
        item.show()
        item.setZValue(10)
        self._embedded_placeholder = placeholder
        self.sync_embedded_graphics_item()

    def sync_embedded_graphics_item(self):
        placeholder = getattr(self, "_embedded_placeholder", None)
        if placeholder is None or not self.is_embedded or self.parent._elements_container is None:
            return

        item = self.graphicsItem()
        rect = item.boundingRect()
        placeholder.setFixedSize(math.ceil(rect.width()), math.ceil(rect.height()))

        pos = placeholder.mapTo(self.parent._elements_container, QtCore.QPoint(0, 0))
        item.setPos(self.parent.INNER_MARGIN + pos.x(), self.parent.TITLE_OFFSET + pos.y())
        self.refresh_terminal_positions()

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

        local_element = self._terminal_element(localTerm)
        remote_element = self._terminal_element(remoteTerm)
        if local_element is None or remote_element is None:
            return

        local_element.value = remote_element

    def disconnected(self, localTerm, remoteTerm):
        if not localTerm.isInput() or not remoteTerm.isOutput():
            return

        local_element = self._terminal_element(localTerm)
        if local_element is None:
            return

        parameter = self._init_parameters().get(localTerm.name())
        if parameter is None or parameter.default is inspect._empty:
            return

        local_element.value = parameter.default

    @staticmethod
    def _terminal_element(term):
        node = term.node()
        element = getattr(node, node.terminal_element_name(term.name()), None)
        return element if hasattr(element, "value") else None

    def terminal_element_name(self, terminal_name):
        return terminal_name

    def get_flowchart_visible_nodes(self):
        if self.parent is not None:
            return self.parent.get_flowchart_visible_nodes()

        scene = self.graphicsItem().scene()
        if scene is None:
            return []
        return [item.node for item in scene.items() if hasattr(item, "node") and item.node is not self and item.isVisible()]

    def c_update(self, **kwargs):
        return {}
