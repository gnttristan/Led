import numpy as np

from backend.config import FREQ_BINS
from backend.rainbow.config import RAINBOW_INV_FRACTION
from backend.rainbow.rainbow import Rainbow
from frontend.components.elements.color_picker import ColorPicker
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.components.elements.dials import LinearDial
from frontend.enums.gradiant.gradiant_mode import GradiantMode
from frontend.overrides.CNode import CNode


class GradiantRainbowNode(Rainbow, CNode):
    nodeName = "GradiantRainbow"

    def __init__(
            self,
            n_points: int = FREQ_BINS,
            inv_fraction: int | float = RAINBOW_INV_FRACTION,
            color_in=(255, 0, 0),
            color_out=(255, 0, 0),
            cycle=1,
            mode: GradiantMode = GradiantMode.LINEAR,
            render: bool = True,
            is_child: bool = False,
            alias: str | None = None,
    ) -> None:
        terminals = {
            "data": {"io": "out"},
        }

        CNode.__init__(self, self.nodeName, terminals=terminals, render=render, is_child=is_child, alias=alias)

        self.n_points = n_points
        self.inv_fraction = LinearDial(self, "inv_fraction", 0, 1, ElementValue(inv_fraction))
        self.color_in = ColorPicker(self, "color_in", ElementValue(color_in))
        self.color_out = ColorPicker(self, "color_out", ElementValue(color_out))
        self.mode = Element(self, "mode", ElementValue(mode))
        self.cycle = LinearDial(self, "cycle", 0, 10, ElementValue(cycle))
        Rainbow.__init__(
            self,
            self.inv_fraction.value,
            self.n_points,
            color_in=self.color_in.value,
            color_out=self.color_out.value,
            cycle=self.cycle.value,
        )
        self.data = Element(self, "data", ElementValue(self.data))
        self.color_in.valueChanged.connect(self.refresh_rainbow)
        self.color_out.valueChanged.connect(self.refresh_rainbow)
        self.cycle.valueChanged.connect(self.refresh_rainbow)
        self.refresh_rainbow()


    def c_update(self):
        super().c_update()

    def refresh_rainbow(self):
        rainbow_rgb = self.get_rainbow_rbg(
            self.n_points,
            self.color_in.value,
            self.color_out.value,
            self.cycle.value,
        )

        if self.mode.value == GradiantMode.MIRROR:
            self.data.value[:] = np.concatenate(((x:=rainbow_rgb[::2]), x[::-1]))
            return
        self.data.value[:] = rainbow_rgb
