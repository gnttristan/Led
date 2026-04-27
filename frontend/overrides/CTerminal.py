import numpy as np
from PyQt5 import QtWidgets
from pyqtgraph.flowchart.Terminal import Terminal


class CTerminal(Terminal):
    connexion_constraints = {
        np.ndarray: lambda obj, obj2: obj.shape[-1] == obj2.shape[-1],
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

        output_owner = getattr(output_node, "obj", output_node)
        input_owner = getattr(input_node, "obj", input_node)

        if hasattr(output_owner, output_term.name()) and hasattr(input_owner, input_term.name()):
            output_value = getattr(output_owner, output_term.name()).value
            input_value = getattr(input_owner, input_term.name()).value

            if not isinstance(output_value, type(input_value)):
                self.display_error_message(
                    f"Incompatible terminal types: {type(output_value).__name__} -> {type(input_value).__name__}"
                )
                return None

            # constraint = self.connexion_constraints.get(type(input_value))
            # if constraint is not None and not constraint(input_value, output_value):
            #     self.display_error_message(
            #         f"Incompatible terminal values for {output_term.name()} -> {input_term.name()}"
            #     )
            #     return None

        if input_term.isConnected() and not input_term.connectedTo(output_term):
            print(f"Terminal '{input_term.name()}' is already connected")
            return None

        return Terminal.connectTo(self, term, connectionItem=connectionItem)
