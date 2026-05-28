from PyQt5 import QtWidgets
import numpy as np

from frontend.components.elements.element import Element
from frontend.components.ui.form_row import FormRow
from frontend.overrides.CNode import CNode


class CreateNodeForm(QtWidgets.QDialog):
    def __init__(self, flowchart, node, node_name, node_parameters):
        super().__init__()
        self.flowchart = flowchart
        self.node = node
        self.node_name = node_name
        self.node_parameters = node_parameters

        self.setWindowTitle("Create Node")
        self.setModal(True)

        self.vbox_layout = QtWidgets.QVBoxLayout(self)

        self.node_name_label = QtWidgets.QLabel()
        self.node_name_label.setText(self.node_name)
        self.vbox_layout.addWidget(self.node_name_label)

        self.form_rows = []
        self.create_button = QtWidgets.QPushButton("Create")
        self.create_button.clicked.connect(self.add_node)
        self.init_for_parameters()
        self.vbox_layout.addWidget(self.create_button)

        self.errors = []
        self.errors_placeholder = QtWidgets.QLabel()
        self.errors_placeholder.setText("\n".join(self.errors))
        self.vbox_layout.addWidget(self.errors_placeholder)

    def init_for_parameters(self):
        element_names = {
            element.name
            for element in self.node.elements
            if isinstance(element, Element)
        }
        for parameter in self.node_parameters:
            if parameter.name not in element_names:
                continue
            form_row = FormRow(self.flowchart, self.node, parameter)
            self.form_rows.append(form_row)
            self.vbox_layout.addWidget(form_row)

    def add_node(self):
        check_ok = self.check_node_constraints()
        if check_ok:
            self.node.init_all()
            self.accept()
            return

        self.errors_placeholder.setText("\n ⚠️ ".join(self.errors))


    def check_node_constraints(self):
        self.errors = []
        for element in self.node.elements:
            corresponding_form_row = next(iter(filter(
                lambda form_row: form_row.element.name == element.name,
                self.form_rows
            )), None)
            if corresponding_form_row is None:
                continue
            element_name, check, err_msg = element.name, *element.check_value(corresponding_form_row.element.value)
            if not check:
                self.errors.append(f"{element_name}: {err_msg}")
            elif corresponding_form_row.element.value is not None:
                element.value = self._coerce_value(element.value, corresponding_form_row.element.value)
                element.after_ui_init(corresponding_form_row.element)

        return len(self.errors) == 0

    @staticmethod
    def _coerce_value(current_value, new_value):
        if isinstance(new_value, CNode):
            return new_value
        if isinstance(current_value, np.ndarray):
            return np.asarray(new_value, dtype=current_value.dtype)
        return new_value if current_value is None else type(current_value)(new_value)
