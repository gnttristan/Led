from types import NoneType
from types import UnionType
from typing import get_args, get_origin

import numpy as np
import inspect
from PyQt5 import QtWidgets

from frontend.components.elements import GradiantModeElement, Interval
from frontend.components.elements.dials import Dial
from frontend.components.elements.element_value import ElementValue
from frontend.components.elements.node_selector.node_selector import NodeSelector
from frontend.components.elements.switch.switch import Switch
from frontend.components.elements.textedit import TextEdit
from frontend.enums.gradiant.gradiant_mode import GradiantMode
from frontend.overrides.CNode import CNode

class FormRow(QtWidgets.QWidget):
    def row_type_to_element(self, p_node, prm):
        value = None if prm.default is inspect.Parameter.empty else prm.default
        type_to_element = {
            str: lambda: TextEdit(p_node, prm.name, ElementValue(value), register_in_node=False),
            int: lambda: TextEdit(p_node, prm.name, ElementValue(value), register_in_node=False),
            float: lambda: TextEdit(p_node, prm.name, ElementValue(value), register_in_node=False),
            tuple: lambda: Interval(p_node, prm.name, ElementValue(value), register_in_node=False),
            bool: lambda: Switch(p_node, prm.name, ElementValue(value), register_in_node=False),
            GradiantMode: lambda: GradiantModeElement(p_node, prm.name, ElementValue(value), register_in_node=False),
            CNode: lambda: NodeSelector(p_node, prm.name, ElementValue(None), selection_nodes=self.flowchart.visible_nodes, register_in_node=False),
            np.ndarray: lambda: NodeSelector(p_node, prm.name, ElementValue(value), selection_nodes=self.flowchart.visible_nodes, register_in_node=False),
            NoneType: lambda: TextEdit(p_node, prm.name, ElementValue(value), register_in_node=False)
        }

        annotation = prm.annotation
        annotation_origin = get_origin(annotation)
        annotation_args = get_args(annotation)
        if annotation_origin is UnionType:
            annotation = next((arg for arg in annotation_args if arg is not NoneType), NoneType)
        if annotation in type_to_element:
            return type_to_element[annotation]()
        return type_to_element[type(value)]()

    def __init__(self, flowchart, parent_node, parameter, required=True):
        super().__init__()
        self.flowchart = flowchart
        self.parent_node = parent_node
        self.parameter = parameter
        self.required = required
        self.element = None
        self.hbox_layout = QtWidgets.QHBoxLayout(self)
        self.hbox_layout.setContentsMargins(0, 0, 0, 0)
        self.init_corresponding_element()

    def init_corresponding_element(self):
        self.element = self.row_type_to_element(self.parent_node, self.parameter)

        self.element.setParent(self)
        self.hbox_layout.addWidget(self.element)
