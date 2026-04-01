import numpy as np
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from pyqtgraph.Qt import QtWidgets

from backend.pipelines.pipeline import AudioPipeline
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.components.node_selector.node_selector import NodeSelector
from frontend.components.textedit.textedit import TextEdit
from frontend.nodes.cnode import CNode

class OperatorPipelineNode(CNode, AudioPipeline):
    nodeName = "OperatorPipeline"
    # operations_allowed = ["+", "-", "*", "/"]
    successMessage = lambda self: "Operation compiled with success"
    errorMessage = lambda self, e: f"Operation compile failed: {e}"

    def __init__(self, arguments, length):
        self.terminals_dict = {
            "data": {"io": "out"}
        }

        self.arguments = arguments
        self.operation_element_names = [self.resolve_element_name(arg) for arg in arguments]

        self.update_terminal()

        super().__init__(node_name=self.nodeName, terminals=self.terminals_dict.copy())

        self.operation_elements = self.define_operation_elements(arguments)

        self.data = Element(self, "data", ElementValue(np.zeros(length)))

        self.operation_state_label = QtWidgets.QLabel(self.successMessage())
        label_font = QFont(self.operation_state_label.font())
        label_font.setPointSize(8)
        self.operation_state_label.setFont(label_font)
        self.operation_state_label.setAlignment(QtCore.Qt.AlignCenter)
        self.elements.append(self.operation_state_label)

    def evaluate_arguments_callback(self):
        try:
            self.data.value[:] = self.evaluate_arguments()
            self.operation_state_label.setText(self.successMessage())
            self.operation_state_label.setStyleSheet("color: green;")
        except SyntaxError as e:
            self.operation_state_label.setText(self.errorMessage(e))
            self.operation_state_label.setStyleSheet("color: red;")

    def c_update(self):
        pass

    def resolve_element_name(self, arg):
        if isinstance(arg, Element):
            return f"{arg.node.name()}:{arg.name}".lower()
        return str(arg)

    def resolve_token(self, token):
        if isinstance(token, Element):
            return self.resolve_token(token.value)
        if isinstance(token, np.ndarray):
            return f"np.array({(
                str(np.char.add(token.astype(str), ","))
                .replace("'", "")
                .replace("\n", "")
            )})"
        return str(token)

    def evaluate_arguments(self):
        expression = []

        for element in self.operation_elements:
            expression.append(self.resolve_token(element.value))
        return eval(" ".join(expression))

    def update_terminal(self):
        args_elements_indexes = list(map(
            lambda x: x[0], filter(
                lambda y: isinstance(y[1], Element),
                enumerate(self.arguments)
            )
        ))
        for arg_element_index in args_elements_indexes:
            self.terminals_dict[self.operation_element_names[arg_element_index]] = {"io": "in"}
        self.pending_terminals = dict(self.terminals_dict)
        # self.init_terminals()

    def define_operation_elements(self, arguments):
        elements = []

        for name, arg in zip(self.operation_element_names, arguments):
            if isinstance(arg, Element):
                element = NodeSelector(
                    self,
                    name,
                    ElementValue(arg),
                    selection_nodes=self.get_flowchart_visible_nodes
                )
            elif isinstance(arg, str):
                element = TextEdit(self, name, ElementValue(arg))
                element.text_edit.textEdited.connect(self.evaluate_arguments_callback)
            else:
                element = TextEdit(self, name, ElementValue(str(arg)))
                element.text_edit.textEdited.connect(self.evaluate_arguments_callback)
            setattr(self, name, element)
            elements.append(element)

        return elements

    def get_flowchart_visible_nodes(self):
        return self.graphicsItem().getViewBox().widget.chart.visible_nodes
