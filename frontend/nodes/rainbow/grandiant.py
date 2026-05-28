import numpy as np

from config import FREQ_BINS
from frontend.components.elements.color_picker import ColorPicker
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.components.elements.textedit import TextEdit
from frontend.overrides.CNode import CNode


class GradiantNode(CNode):
    nodeName = "Grandiant"

    def __init__(
        self,
        n_points: int = FREQ_BINS,
        color_in=(255, 0, 0),
        color_out=(0, 0, 255),
        render: bool = True,
            parent: CNode | None = None,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals=terminals, render=render, parent=parent, alias=alias)

        self.n_points = TextEdit(self, "n_points", ElementValue(n_points))
        self.color_in = ColorPicker(self, "color_in", ElementValue(color_in))
        self.color_out = ColorPicker(self, "color_out", ElementValue(color_out))
        self.data = Element(self, "data", ElementValue(np.zeros((int(self.n_points.value), 3), dtype=int)))

        self.n_points.valueChanged.connect(self.refresh_grandiant)
        self.color_in.valueChanged.connect(self.refresh_grandiant)
        self.color_out.valueChanged.connect(self.refresh_grandiant)
        self.refresh_grandiant()

    def refresh_grandiant(self):
        try:
            n_points = int(self.n_points.value)
        except (TypeError, ValueError):
            return

        if self.data.value.shape != (n_points, 3):
            self.data.value = np.zeros((n_points, 3), dtype=int)

        color_in = np.asarray(self.color_in.value, dtype=float)
        color_out = np.asarray(self.color_out.value, dtype=float)
        offsets = np.linspace(0.0, 1.0, n_points)[:, None]
        self.data.value[:] = np.clip(
            np.rint(color_in * (1.0 - offsets) + color_out * offsets),
            0,
            255,
        ).astype(int)
