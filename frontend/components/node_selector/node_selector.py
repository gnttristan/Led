from pyqtgraph.Qt import QtCore, QtWidgets

from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.overrides.CComboBox import CComboBox


class NodeSelector(Element):
    def __init__(self, node, name, value=None, selection_nodes=[], selection_elements=[], **kwargs):
        super().__init__(node, name, value)
        self.selection_nodes = ElementValue(selection_nodes)
        self.selection_elements = ElementValue(selection_elements)
        
        if not node.render:
            return

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.controls_container = QtWidgets.QWidget()
        self.controls_layout = QtWidgets.QHBoxLayout(self.controls_container)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.setSpacing(4)

        self.selection_nodes_combobox = CComboBox()
        self.selection_nodes_combobox.setFixedSize(100, 20)
        self.selection_nodes_combobox.setContentsMargins(0, 0, 0, 0)
        self.selection_nodes_combobox.addItems(["null"])
        self.selection_nodes_combobox.arrowClicked.connect(self.refresh_selection_nodes)
        self.selection_nodes_combobox.currentIndexChanged.connect(self.set_node_value)
        self.controls_layout.addWidget(self.selection_nodes_combobox)

        self.selection_elements_combobox = QtWidgets.QComboBox()
        self.selection_elements_combobox.setFixedSize(100, 20)
        self.selection_elements_combobox.setContentsMargins(0, 0, 0, 0)
        self.selection_elements_combobox.addItems(["null"] + self.selection_elements.value)
        self.selection_elements_combobox.currentIndexChanged.connect(self.set_element_value)
        self.controls_layout.addWidget(self.selection_elements_combobox)

        self.container_vchange_layout.addWidget(self.controls_container)

    def extract_selection_node_names(self):
        return list(map(lambda x: x.name(), self.selection_nodes.value))


    def refresh_selection_nodes(self):
        selected_text = self.selection_nodes_combobox.currentText()
        self.selection_nodes_combobox.blockSignals(True)
        self.selection_nodes_combobox.clear()
        self.selection_nodes_combobox.addItems(["null"] + self.extract_selection_node_names())
        ##!!
        if selected_text in ["null"] + self.selection_nodes.value:
            self.selection_nodes_combobox.setCurrentText(selected_text)
        self.selection_nodes_combobox.blockSignals(False)

    def set_node_value(self, item):
        print(item)

    def set_element_value(self, item):
        print(item)
