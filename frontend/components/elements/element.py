import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5 import QtCore, QtWidgets

from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class Element(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal(object)

    @staticmethod
    def _format_ndarray(x: np.ndarray) -> str:
        if x.size == 0:
            return f"empty shape:{x.shape}"
        if x.size == 1:
            scalar = x.reshape(-1)[0]
            if isinstance(scalar, (float, np.floating)):
                return f"{float(scalar):.2f}"
            return str(scalar)
        return (
            f"min:{float(np.min(x)):.2f} "
            f"avg:{float(np.mean(x)):.2f} "
            f"max:{float(np.max(x)):.2f} "
            f"shape:{x.shape}"
        )

    str_trsf = {
        str: lambda x: x,
        int: lambda x: str(x),
        bool: lambda x: str(x),
        float: lambda x: f"{x:.2f}",
        list: lambda x: f"{x}",
        CNode: lambda x: x.nodeName,
        np.ndarray: lambda x: Element._format_ndarray(x),
    }

    @classmethod
    def format_value(cls, value):
        if isinstance(value, Element) or isinstance(value, ElementValue):
            value = value.value
        if isinstance(value, tuple):
            return "(" + ", ".join(cls.format_value(v) for v in value) + ")"
        if isinstance(value, list):
            return "[" + ", ".join(cls.format_value(v) for v in value) + "]"
        for value_type, formatter in cls.str_trsf.items():
            if isinstance(value, value_type):
                return formatter(value)
        return str(value)

    @staticmethod
    def connect_terminal(self, element):
        ##!! ToDo Look in depth and maybe change [#1]
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
            QtCore.QTimer.singleShot(25, lambda: Element.connect_terminal(self, element))
            return
        if target_terminal.isConnected() and target_terminal.connectedTo(source_terminal):
            return
        source_terminal.connectTo(target_terminal)

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

        super().__init__()

        if isinstance(value, ElementValue):
            self._value_ref = value
            value = value.value

        if isinstance(value, Element):
            self._value_ref = ElementValue(lambda: value.value)
            self.value = value.value
            if self.link_terminal and self.node.parent is None:
                QtCore.QTimer.singleShot(0, lambda: self.connect_terminal(self, value))
        else:
            if isinstance(value, CNode):
                value.parent = self.node
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, CNode):
                        item.parent = self.node
            self._value = value

        # HBox for elements
        self.hbox_elements = QtWidgets.QHBoxLayout()
        self.hbox_elements.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hbox_elements.setContentsMargins(0, 0, 0, 0)
        self.hbox_elements.setSpacing(0)
        self.setLayout(self.hbox_elements)

        # Font
        font = QFont()
        font.setPointSize(8)

        terminal_name = self.name.lower()
        terminal_opts = node.pending_terminals.get(terminal_name)

        left_terminal_placeholder = QtWidgets.QWidget()
        left_terminal_placeholder.setFixedWidth(node.TERMINAL_WIDTH)
        self.hbox_elements.addWidget(left_terminal_placeholder)

        # Element name
        name_label = QtWidgets.QLabel()
        name_label.setText(name)
        name_label.setFixedWidth(100)
        name_label.setFont(font)
        self.hbox_elements.addWidget(name_label)

        # Element value
        self.hbox_elements.addWidget(self.build_value_widget(self.value, font))
        self.hbox_elements.addStretch()

        ##!! ToDo toChange
        if callable(getattr(self._value_ref, "_value", None)):
            self._dynamic_label_timer = QtCore.QTimer(self)
            self._dynamic_label_timer.timeout.connect(self.refresh_value_label)
            self._dynamic_label_timer.start(250)

        # Element value widget change
        self.container_vchange = QtWidgets.QWidget()
        self.container_vchange.setMinimumWidth(100)
        self.container_vchange_layout = QtWidgets.QHBoxLayout(self.container_vchange)
        self.container_vchange_layout.setContentsMargins(0, 0, 0, 0)
        self.container_vchange_layout.setSpacing(0)
        self.hbox_elements.addWidget(self.container_vchange)

        right_terminal_placeholder = QtWidgets.QWidget()
        right_terminal_placeholder.setFixedWidth(node.TERMINAL_WIDTH)
        self.hbox_elements.addWidget(right_terminal_placeholder)

        self.terminal_name = terminal_name if terminal_opts else None
        self.terminal_io = terminal_opts.get("io") if terminal_opts else None
        self.terminal_placeholder = {
            "in": left_terminal_placeholder,
            "out": right_terminal_placeholder,
        }.get(self.terminal_io)

        if register_in_node:
            self.node.elements.append(self)

    @property
    def value(self):
        if self._value_ref is not None:
            return self._value_ref.value
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._value_ref is not None:
            if not callable(getattr(self._value_ref, "_value", None)):
                self._value_ref.value = value
        self.refresh_value_label()
        self.valueChanged.emit(self.value)

    def build_value_widget(self, value, font):
        if isinstance(value, list) and any(isinstance(item, CNode) for item in value):
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            for item in value:
                layout.addWidget(self.build_value_widget(item, font))
            return container

        if isinstance(value, CNode):
            container = QtWidgets.QWidget()
            value._embedded_container = container
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            header = QtWidgets.QWidget()
            header_layout = QtWidgets.QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(4)

            title = QtWidgets.QLabel(value.nodeName)
            title.setFont(font)
            header_layout.addWidget(title)

            toggle_button = QtWidgets.QToolButton()
            toggle_button.setCheckable(True)
            toggle_button.setArrowType(QtCore.Qt.RightArrow)
            toggle_button.setFixedSize(14, 14)
            toggle_button.setStyleSheet("padding: 0px; margin: 0px;")
            header_layout.addWidget(toggle_button)
            header_layout.addStretch()
            layout.addWidget(header)

            body = QtWidgets.QWidget()
            body_layout = QtWidgets.QVBoxLayout(body)
            body_layout.setContentsMargins(0, 0, 0, 0)
            body_layout.setSpacing(0)
            body.setVisible(False)
            layout.addWidget(body)

            # value.render = False

            def sync_child_elements():
                for element in value.elements:
                    if body_layout.indexOf(element) == -1:
                        body_layout.addWidget(element)

            def on_toggle(is_open):
                value.render = is_open
                toggle_button.setArrowType(QtCore.Qt.DownArrow if is_open else QtCore.Qt.RightArrow)
                if is_open:
                    sync_child_elements()
                body.setVisible(is_open)
                body.adjustSize()
                container.adjustSize()
                self.adjustSize()
                value.refresh_terminal_positions()
                self.node.refresh_terminal_positions()
                QtCore.QTimer.singleShot(0, self.node.refresh_terminal_positions)

            toggle_button.toggled.connect(on_toggle)

            return container

        value_label = QtWidgets.QLabel()
        value_label.setText(self.format_value(value))
        value_label.setMinimumWidth(80)
        value_label.setFont(font)
        self.value_label = value_label
        return value_label

    def refresh_value_label(self):
        if self.value_label is not None:
            self.value_label.setText(self.format_value(self.value))

    def attach_terminal(self, title_offset, inner_margin):
        if self.terminal_placeholder is None:
            return

        terminal = self.node[self.terminal_name].graphicsItem()
        terminal.label.hide()
        terminal.setZValue(100)
        if self.node.parent is not None:
            self.node.graphicsItem().setZValue(self.node.parent.graphicsItem().zValue() + 10)
        placeholder_geometry = self.terminal_placeholder.geometry()

        container = getattr(self.node, "_embedded_container", None)
        parent_widget = self.parentWidget()
        is_in_container = False
        while parent_widget is not None:
            if parent_widget is container:
                is_in_container = True
                break
            parent_widget = parent_widget.parentWidget()
        if is_in_container:
            element_pos = self.mapTo(container, QtCore.QPoint(0, 0))
            if self.node.parent is not None and self.node.parent._elements_container is not None:
                element_pos += container.mapTo(self.node.parent._elements_container, QtCore.QPoint(0, 0))
        else:
            element_pos = self.geometry().topLeft()
        anchor_y = title_offset + element_pos.y() + placeholder_geometry.center().y()
        anchor_x = inner_margin + element_pos.x() + placeholder_geometry.x()
        if self.terminal_io == "out":
            anchor_x += placeholder_geometry.width()

        if self.node.parent is not None and is_in_container:
            anchor = self.node.graphicsItem().mapFromScene(
                self.node.parent.graphicsItem().mapToScene(anchor_x, anchor_y)
            )
            anchor_x = anchor.x()
            anchor_y = anchor.y()

        if self.terminal_io == "in":
            terminal.setAnchor(anchor_x, anchor_y)
        else:
            terminal.setAnchor(anchor_x, anchor_y)

    def check_value(self, placeholder_value):
        return True, None
