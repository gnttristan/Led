import numpy as np
from PyQt5 import QtWidgets
from pyqtgraph.flowchart.Terminal import Terminal


class CTerminal(Terminal):
    _MISSING = object()

    @staticmethod
    def is_compatible(output_value, input_value):
        type_compatibility = {
            np.ndarray: lambda out_v, in_v: isinstance(out_v, np.ndarray) and out_v.shape == in_v.shape,
        }
        return (type_compatibility.get(type(output_value),
            lambda out_v, in_v: isinstance(out_v, type(in_v))
        )(output_value, input_value))

    @staticmethod
    def display_error_message(message):
        QtWidgets.QMessageBox.critical(None, "Connection Error", message)
        raise Exception(message)

    def connectTo(self, term, connectionItem=None):
        output_term, input_term = self._ordered_terms(term)
        output_value = self._terminal_value(output_term)
        input_value = self._terminal_value(input_term)

        if (
            output_value is not self._MISSING
            and input_value is not self._MISSING
            and not self.is_compatible(output_value, input_value)
        ):
            self.display_error_message(
                f"Incompatible terminal types: {type(output_value).__name__} -> {type(input_value).__name__}"
            )
            return None

        if input_term.isConnected() and not input_term.connectedTo(output_term):
            print(f"Terminal '{input_term.name()}' is already connected")
            return None

        return Terminal.connectTo(self, term, connectionItem=connectionItem)

    def _ordered_terms(self, term):
        return (term, self) if self.isInput() else (self, term)

    @staticmethod
    def _terminal_value(term):
        owner = getattr(term.node(), "obj", term.node())
        element_name = owner.terminal_element_name(term.name())
        element = getattr(owner, element_name, CTerminal._MISSING)
        return element.value if hasattr(element, "value") else CTerminal._MISSING
