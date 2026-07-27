from PyQt5 import QtCore, QtWidgets

from frontend.components.elements.element import Element
from frontend.overrides.CNode import CNode


class ChartElement(Element):
    def __init__(
        self,
        node: CNode,
        name: str,
        link_terminal: bool = True,
        register_in_node: bool = True,
        show_chart_button: bool = True,
    ) -> None:
        super().__init__(node, name, "", link_terminal=link_terminal, register_in_node=register_in_node)
        self.window = None

        if not show_chart_button:
            return

        self.chart_button = QtWidgets.QToolButton()
        self.chart_button.setCheckable(True)
        self.chart_button.setArrowType(QtCore.Qt.RightArrow)
        self.chart_button.setFixedSize(14, 14)
        self.chart_button.setStyleSheet("padding: 0px; margin: 0px;")
        self.container_vchange_layout.addWidget(self.chart_button)
        self.chart_button.toggled.connect(self._toggle_chart)

    def build_value_widget(self, value, font):
        del value, font
        return QtWidgets.QWidget()

    def _toggle_chart(self, is_open):
        if is_open:
            if self.window is None:
                self.node.draw()
            self.window.show()
            self.chart_button.setArrowType(QtCore.Qt.DownArrow)
        else:
            if self.window is not None:
                self.window.hide()
            self.chart_button.setArrowType(QtCore.Qt.RightArrow)
