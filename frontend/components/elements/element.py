import numpy as np
from PyQt5.QtGui import QFont
from PyQt5 import QtCore, QtWidgets

from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class ObservableArray(np.ndarray):
    def __new__(cls, array, on_mutation):
        obj = np.asarray(array).view(cls)
        obj._on_mutation = on_mutation
        return obj

    def __array_finalize__(self, obj):
        self._on_mutation = getattr(obj, "_on_mutation", None)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if self._on_mutation is not None:
            self._on_mutation()


class Element(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal(object)
    arrayValueMutated = QtCore.pyqtSignal()
    TOP = QtCore.Qt.AlignmentFlag.AlignTop
    LEFT_TOP = QtCore.Qt.AlignmentFlag.AlignLeft | TOP

    @staticmethod
    def _format_ndarray(x: np.ndarray) -> str:
        if x.size == 0:
            return f"empty shape:{x.shape}"
        if x.size == 1:
            scalar = x.reshape(-1)[0]
            return f"{float(scalar):.2f}" if isinstance(scalar, (float, np.floating)) else str(scalar)
        return (
            f"min:{float(np.min(x)):.2f} "
            f"avg:{float(np.mean(x)):.2f} "
            f"max:{float(np.max(x)):.2f} "
            f"s:{x.shape}"
        )

    str_trsf = {
        str: lambda x: x,
        int: lambda x: str(x),
        float: lambda x: f"{x:.2f}",
        CNode: lambda x: x.nodeName,
        np.ndarray: lambda x: Element._format_ndarray(x),
    }

    @classmethod
    def format_value(cls, value):
        if isinstance(value, (Element, ElementValue)):
            value = value.value
        if isinstance(value, tuple):
            return "(" + ", ".join(cls.format_value(v) for v in value) + ")"
        if isinstance(value, list):
            return "[" + ", ".join(cls.format_value(v) for v in value) + "]"
        for value_type, formatter in cls.str_trsf.items():
            if isinstance(value, value_type):
                return formatter(value)
        return str(value)

    def connect_terminal(self, element):
        source_terminal = element.node[element.name.lower()]
        target_terminal = self.node[self.name.lower()]
        source_item = source_terminal.graphicsItem()
        target_item = target_terminal.graphicsItem()
        if (
            source_item.getViewBox() is None
            or target_item.getViewBox() is None
            or source_item.connectPoint() is None
            or target_item.connectPoint() is None
        ):
            QtCore.QTimer.singleShot(25, lambda: self.connect_terminal(element))
            return
        if target_terminal.isConnected() and target_terminal.connectedTo(source_terminal):
            return
        source_terminal.connectTo(target_terminal)

    @staticmethod
    def _layout(layout_cls, container=None, spacing=0, alignment=None):
        layout = layout_cls(container) if container is not None else layout_cls()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(spacing)
        if alignment is not None:
            layout.setAlignment(alignment)
        return layout

    @staticmethod
    def _terminal_placeholder(width):
        placeholder = QtWidgets.QWidget()
        placeholder.setFixedWidth(width)
        return placeholder

    def _set_child_parent(self, value):
        values = value if isinstance(value, list) else (value,)
        for item in values:
            if isinstance(item, CNode):
                item.parent = self.node

    def __init__(
        self,
        node: CNode,
        name: str,
        value: object,
        link_terminal: bool = True,
        register_in_node: bool = True,
    ) -> None:
        self.node = node
        self.name = name
        self.link_terminal = link_terminal
        self.value_label = None
        self._value = None
        self._value_ref = None
        self._array_refresh_pending = False

        super().__init__()
        self.setProperty("ledRole", "elementRow")
        self.arrayValueMutated.connect(self._flush_array_value_mutation, QtCore.Qt.QueuedConnection)

        if isinstance(value, ElementValue):
            self._value_ref = value
            value = value.value

        if isinstance(value, Element):
            self.value = value
            if self.link_terminal and self.node.parent is None:
                QtCore.QTimer.singleShot(0, lambda: self.connect_terminal(value))
        else:
            self._set_child_parent(value)
            self._store_value(value)

        self.hbox_elements = self._layout(QtWidgets.QHBoxLayout, spacing=6, alignment=self.LEFT_TOP)
        self.hbox_elements.setContentsMargins(0, 4, 0, 4)
        self.setLayout(self.hbox_elements)

        font = QFont()
        font.setPointSize(9)

        terminal_name = self.name.lower()
        terminal_opts = node.pending_terminals.get(terminal_name)

        left_terminal_placeholder = self._terminal_placeholder(node.TERMINAL_WIDTH)
        self.hbox_elements.addWidget(left_terminal_placeholder)

        name_label = QtWidgets.QLabel(name)
        name_label.setProperty("ledRole", "elementName")
        name_label.setMinimumWidth(104)
        name_label.setMaximumWidth(132)
        name_label.setFont(font)
        self.hbox_elements.addWidget(name_label)

        self.hbox_elements.addWidget(self.build_value_widget(self.value, font), alignment=self.TOP)
        self.hbox_elements.addStretch()

        self.container_vchange = QtWidgets.QWidget()
        self.container_vchange.setProperty("ledRole", "valueControls")
        self.container_vchange.setMinimumWidth(112)
        self.container_vchange_layout = self._layout(QtWidgets.QHBoxLayout, self.container_vchange, spacing=5)
        self.hbox_elements.addWidget(self.container_vchange)

        right_terminal_placeholder = self._terminal_placeholder(node.TERMINAL_WIDTH)
        self.hbox_elements.addWidget(right_terminal_placeholder)

        self.terminal_name = terminal_name if terminal_opts else None
        self.terminal_io = terminal_opts.get("io") if terminal_opts else None
        self.terminal_placeholder = {
            "in": left_terminal_placeholder,
            "out": right_terminal_placeholder,
        }.get(self.terminal_io)
        self.mapped_output_terminal_name = next(
            (
                name
                for name, opts in node.pending_terminals.items()
                if opts.get("io") == "out" and node.terminal_element_name(name) == terminal_name
            ),
            None,
        )
        self.mapped_output_terminal_placeholder = right_terminal_placeholder

        if register_in_node:
            self.node.elements.append(self)

    @property
    def value(self):
        return self._value_ref.value if self._value_ref is not None else self._value

    @value.setter
    def value(self, value):
        if isinstance(value, Element):
            self._value_ref = value
            self._value = self._wrap_observable_array(value.value)
            self.refresh_value_label()
            self.valueChanged.emit(self.value)
            return
        if isinstance(self._value_ref, Element):
            self._value_ref = None
        self._store_value(value)
        self.refresh_value_label()
        self.valueChanged.emit(self.value)

    def _store_value(self, value):
        value = self._wrap_observable_array(value)
        self._value = value
        if isinstance(self._value_ref, ElementValue):
            self._value_ref.value = value

    def _wrap_observable_array(self, value):
        if isinstance(value, np.ndarray):
            return ObservableArray(value, self._schedule_array_value_mutation)
        return value

    def _schedule_array_value_mutation(self):
        if self._array_refresh_pending:
            return
        self._array_refresh_pending = True
        self.arrayValueMutated.emit()

    def _flush_array_value_mutation(self):
        if not self._array_refresh_pending:
            return
        self._array_refresh_pending = False
        self.refresh_value_label()
        self.valueChanged.emit(self.value)

    def _top_container(self, layout_cls=QtWidgets.QVBoxLayout, spacing=0, align_top=True):
        container = QtWidgets.QWidget()
        container.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        return container, self._layout(layout_cls, container, spacing, self.TOP if align_top else None)

    def build_value_widget(self, value, font):
        if isinstance(value, list) and any(isinstance(item, CNode) for item in value):
            container, layout = self._top_container()
            for item in value:
                layout.addWidget(self.build_value_widget(item, font), alignment=self.TOP)
            return container

        if isinstance(value, CNode):
            return self._build_node_widget(value)

        value_label = QtWidgets.QLabel(self.format_value(value))
        value_label.setMinimumWidth(80)
        value_label.setMaximumWidth(220)
        value_label.setWordWrap(False)
        value_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        value_label.setProperty("ledRole", "elementValue")
        value_label.setFont(font)
        self.value_label = value_label
        return value_label

    def _build_node_widget(self, value):
        placeholder = QtWidgets.QWidget()
        placeholder.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        def sync():
            value.embed_in(self.node, placeholder)
            placeholder.updateGeometry()
            self.adjustSize()
            if self.node._elements_container is not None:
                self.node._elements_container.adjustSize()
            self.node.refresh_terminal_positions()

        QtCore.QTimer.singleShot(0, sync)
        QtCore.QTimer.singleShot(25, sync)
        return placeholder

    def refresh_value_label(self):
        if self.value_label is not None:
            self.value_label.setText(self.format_value(self.value))

    def attach_terminal(self, title_offset, inner_margin):
        if self.terminal_placeholder is None and self.mapped_output_terminal_name is None:
            return

        if self.node.parent is not None:
            self.node.graphicsItem().setZValue(self.node.parent.graphicsItem().zValue() + 10)
        element_pos = self.geometry().topLeft()

        if self.terminal_placeholder is not None:
            self._attach_terminal(self.terminal_name, self.terminal_io, self.terminal_placeholder, title_offset, inner_margin, element_pos)
        if self.mapped_output_terminal_name is not None and self.mapped_output_terminal_name != self.terminal_name:
            self._attach_terminal(self.mapped_output_terminal_name, "out", self.mapped_output_terminal_placeholder, title_offset, inner_margin, element_pos)

    def _attach_terminal(self, terminal_name, terminal_io, placeholder, title_offset, inner_margin, element_pos):
        terminal = self.node[terminal_name].graphicsItem()
        terminal.label.hide()
        terminal.setZValue(100)
        placeholder_geometry = placeholder.geometry()
        anchor_y = title_offset + element_pos.y() + placeholder_geometry.center().y()
        anchor_x = inner_margin + element_pos.x() + placeholder_geometry.x()
        if terminal_io == "out":
            anchor_x += placeholder_geometry.width()
        terminal.setAnchor(anchor_x, anchor_y)

    def check_value(self, placeholder_value):
        return True, None

    def after_ui_init(self, placeholder_element):
        pass
