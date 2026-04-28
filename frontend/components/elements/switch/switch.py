from pyqt_switch import PyQtSwitch

from frontend.components.elements.element import Element
from frontend.overrides.CNode import CNode


class Switch(Element):
    def __init__(self, node: CNode, name: str, value: object = None, **kwargs: object) -> None:
        super().__init__(node, name, bool(value), **kwargs)

        self.switch = PyQtSwitch()
        self._set_switch_checked(bool(self.value))
        self.switch.toggled.connect(self._on_toggled)
        self.container_vchange_layout.addWidget(self.switch)

    def _on_toggled(self, checked: bool) -> None:
        self.value = checked

    def _set_switch_checked(self, checked: bool) -> None:
        # pyqt-switch does not expose a public setChecked API.
        circle = getattr(self.switch, "_PyQtSwitch__circle", None)
        if circle is not None:
            circle.setChecked(checked)


