import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from pyqtgraph.Qt import QtCore, QtWidgets

from frontend.nodes.cnode import CNode


class Element(QtWidgets.QWidget):
    str_trsf = {
        str: lambda x: x,
        int: lambda x: str(x),
        bool: lambda x: str(x),
        float: lambda x: f"{x:.2f}",
        list: lambda x: f"{x}",
        CNode: lambda x: x.nodeName,
        np.ndarray: lambda x: f"{x.shape}",
    }

    @classmethod
    def format_value(cls, value):
        for value_type, formatter in cls.str_trsf.items():
            if isinstance(value, value_type):
                return formatter(value)
        return str(value)

    @staticmethod
    def link_terminal(self, element):
        element.node[element.name.lower()].connectTo(self.node[self.name.lower()])

    @staticmethod
    def define_node_as_child(self):
        self.node.is_child = True

    def __init__(self, node, name, value):
        self.node = node
        self.name = name
        self.value_label = None

        if isinstance(value, Element):
            self.value = value.value
            QtCore.QTimer.singleShot(0, lambda: self.link_terminal(self, value))
        else:
            if isinstance(value, CNode):
                self.node.is_child = True
            self.value = value

        if not node.render:
            return

        super().__init__()

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

        self.node.elements.append(self)

    def build_value_widget(self, value, font):
        if isinstance(value, CNode):
            container = QtWidgets.QWidget()
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

            value.render = False

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
                self.node.refresh_terminal_positions()
                QtCore.QTimer.singleShot(0, self.node.refresh_terminal_positions)

            toggle_button.toggled.connect(on_toggle)

            return container

        value_label = QtWidgets.QLabel()
        value_label.setText(self.format_value(value))
        value_label.setMinimumWidth(40)
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
        placeholder_geometry = self.terminal_placeholder.geometry()
        anchor_y = title_offset + self.geometry().y() + placeholder_geometry.center().y()
        anchor_x = inner_margin + self.geometry().x() + placeholder_geometry.x()

        if self.terminal_io == "in":
            terminal.setAnchor(anchor_x, anchor_y)
        else:
            terminal.setAnchor(anchor_x + placeholder_geometry.width(), anchor_y)
