import numpy as np
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.flowchart.Terminal import Terminal


class CTerminal(Terminal):
    connexion_constraints = {
        np.ndarray: lambda obj, obj2: obj.shape == obj2.shape,
    }

    @staticmethod
    def display_error_message(message):
        message_box = QtWidgets.QMessageBox()
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        message_box.setWindowTitle("Connection Error")
        message_box.setText(message)
        message_box.exec_()
        raise Exception(message)

    def connectTo(self, term, connectionItem=None):
        output_term, input_term = self, term
        if self.isInput():
            output_term, input_term = term, self

        output_node = output_term.node()
        input_node = input_term.node()

        if hasattr(output_node, "obj") and hasattr(input_node, "obj"):
            output_value = getattr(output_node.obj, output_term.name()).value
            input_value = getattr(input_node.obj, input_term.name()).value

            if not isinstance(output_value, type(input_value)):
                self.display_error_message(
                    f"Incompatible terminal types: {type(output_value).__name__} -> {type(input_value).__name__}"
                )
                return None

            constraint = self.connexion_constraints.get(type(input_value))
            if constraint is not None and not constraint(input_value, output_value):
                self.display_error_message(
                    f"Incompatible terminal values for {output_term.name()} -> {input_term.name()}"
                )
                return None

        return Terminal.connectTo(self, term, connectionItem=connectionItem)
