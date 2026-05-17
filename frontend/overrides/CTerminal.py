import numpy as np
from PyQt5 import QtWidgets
from pyqtgraph.flowchart.Terminal import Terminal


class CTerminal(Terminal):
    _MISSING = object()
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
        output_term, input_term = self._ordered_terms(term)
        output_value = self._terminal_value(output_term)
        input_value = self._terminal_value(input_term)

        if output_value is not self._MISSING and input_value is not self._MISSING:
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

    def _ordered_terms(self, term):
        if self.isInput():
            return term, self
        return self, term

    @staticmethod
    def _terminal_value(term):
        owner = getattr(term.node(), "obj", term.node())
        element = getattr(owner, term.name(), None)
        if element is None or not hasattr(element, "value"):
            return CTerminal._MISSING
        return element.value
