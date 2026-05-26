from typing import Callable, Sequence, List

from PyQt5 import QtCore, QtWidgets

from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode
from frontend.overrides.CComboBox import CComboBox


class NodeSelector(Element):
    def __init__(
        self,
        node: CNode,
        name: str,
        value: object = None,
        selection_nodes: Sequence[CNode] | Callable[[], Sequence[CNode]] = [],
        selection_elements: Sequence[str] | Callable[[], Sequence[str]] = [],
        **kwargs: object,
    ) -> None:
        initial_element = value
        while isinstance(initial_element, ElementValue):
            initial_element = initial_element.value
        if not isinstance(initial_element, Element):
            initial_element = None

        super().__init__(node, name, value, **kwargs)
        self.selection_nodes = ElementValue(selection_nodes)
        self.selection_elements = ElementValue(selection_elements)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.controls_container = QtWidgets.QWidget()
        self.controls_layout = QtWidgets.QHBoxLayout(self.controls_container)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.setSpacing(4)

        self.selection_nodes_combobox = CComboBox()
        self.selection_nodes_combobox.setFixedSize(100, 20)
        self.selection_nodes_combobox.setContentsMargins(0, 0, 0, 0)
        self.selection_nodes_combobox.setMinimumContentsLength(10)
        self.selection_nodes_combobox.view().setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.selection_nodes_combobox.addItems(["null"])
        self.selection_nodes_combobox.popupAboutToShow.connect(self.refresh_selection_nodes)
        self.selection_nodes_combobox.currentIndexChanged.connect(self.set_node_value)
        self.controls_layout.addWidget(self.selection_nodes_combobox)

        self.selected_node: CNode | None = None
        self.selected_elements: List[Element | None] = []

        self.selection_elements_combobox = CComboBox()
        self.selection_elements_combobox.setFixedSize(100, 20)
        self.selection_elements_combobox.setContentsMargins(0, 0, 0, 0)
        self.selection_elements_combobox.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.selection_elements_combobox.setMinimumContentsLength(10)
        self.selection_elements_combobox.view().setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.selection_elements_combobox.addItems(["null"] + self.selection_elements.value)
        self.selection_elements_combobox.currentIndexChanged.connect(self.set_element_value)
        self.controls_layout.addWidget(self.selection_elements_combobox)

        self.selected_element = None


        self.container_vchange_layout.addWidget(self.controls_container)
        if initial_element is not None:
            self.set_default_element(initial_element)

    def extract_selection_node_names(self):
        return list(map(lambda x: x.name(), self.selection_nodes.value))

    def extract_selection_element_names(self):
        return list(map(
            lambda x: x.name,
            list(filter(lambda x: isinstance(x, Element), self.selected_node.elements))
        ))


    def refresh_selection_nodes(self):
        selected_text = self.selection_nodes_combobox.currentText()
        node_names = ["null"] + self.extract_selection_node_names()
        if self.selected_node is not None and self.selected_node.name() not in node_names:
            node_names.append(self.selected_node.name())
        self.selection_nodes_combobox.blockSignals(True)
        self.selection_nodes_combobox.clear()
        self.selection_nodes_combobox.addItems(node_names)
        if selected_text in node_names:
            self.selection_nodes_combobox.setCurrentText(selected_text)
        self.selection_nodes_combobox.blockSignals(False)

    def set_node_value(self, item):
        if item == 0:
            self.selected_node = None
            self.selected_elements = []
            self.selection_elements_combobox.clear()
            self.selection_elements_combobox.addItems(["null"])
            self.set_element_value(0)
            return
        else:
            self.selection_nodes_combobox.currentIndexChanged.disconnect(self.set_node_value)
            selection_nodes = self.selection_nodes.value
            self.selected_node = (
                selection_nodes[item - 1]
                if item - 1 < len(selection_nodes)
                else self.selected_node
            ) # Because of the null element
            self.selected_elements = self.selected_node.elements
            self.selection_elements_combobox.clear()

        element_names = ["null"] + self.extract_selection_element_names()
        self.selection_elements_combobox.addItems(element_names)
        self.selection_nodes_combobox.currentIndexChanged.connect(self.set_node_value)
        self.set_element_value(0)


    def set_element_value(self, element_total):
        if element_total <= 0: # 0 if null, -1 if no elements in self.selection_elements_combobox
            self.value = None
            return

        self.selected_element = self.selected_elements[element_total - 1] # Because of the null element
        self.value = lambda : self.selected_element.value

    def set_default_element(self, element):
        self.selected_node = element.node
        self.selected_elements = self.selected_node.elements
        self.selected_element = element

        self.refresh_selection_nodes()
        self.selection_nodes_combobox.setCurrentText(self.selected_node.name())

        element_names = ["null"] + self.extract_selection_element_names()
        self.selection_elements_combobox.blockSignals(True)
        self.selection_elements_combobox.clear()
        self.selection_elements_combobox.addItems(element_names)
        self.selection_elements_combobox.setCurrentText(element.name)
        self.selection_elements_combobox.blockSignals(False)
        self.value = lambda : self.selected_element.value
