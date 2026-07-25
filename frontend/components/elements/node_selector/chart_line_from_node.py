import random

from frontend.components.elements.node_selector.node_selector import NodeSelector
from frontend.components.partials.color_picker_button import ColorPickerButton
from frontend.overrides.CNode import CNode


class ChartLineNodeSelector(NodeSelector):
    def __init__(self, node: CNode, name: str, value=None, **kwargs: object) -> None:
        super().__init__(node, name, value, **kwargs)
        self.color_picker = ColorPickerButton(
            f"{name}_color",
            tuple(random.randint(0, 255) for _ in range(3)),
            self,
        )
        self.color_picker.setFixedSize(30, 20)
        self.controls_layout.addWidget(self.color_picker)

    @property
    def color(self):
        return self.color_picker.value
