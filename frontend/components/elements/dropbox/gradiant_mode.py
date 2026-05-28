from frontend.components.elements.dropbox.dropbox import Dropbox
from frontend.enums.gradiant.gradiant_mode import GradiantMode
from frontend.overrides.CNode import CNode


class GradiantModeElement(Dropbox):
    modes = [mode.name for mode in GradiantMode]

    def __init__(self, node: CNode, name: str, value: object = None, **kwargs: object) -> None:
        super().__init__(node, name, value, items=self.modes, **kwargs)
        self.gradiant_mode_combobox = self.combobox

        if isinstance(self.value, GradiantMode):
            self.combobox.setCurrentText(self.value.name)

    def on_item_changed(self, item: str) -> None:
        self.value = GradiantMode[item]
