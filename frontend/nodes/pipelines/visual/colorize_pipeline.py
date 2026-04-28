import numpy as np

from backend.pipelines.pipeline import VisualPipeline
from config import FREQ_BINS
from frontend.components.elements.color_picker import ColorPicker
from frontend.components.elements.dials import LinearDial
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class ColorizePipelineNode(VisualPipeline, CNode):
    nodeName = "ColorizePipeline"

    def __init__(
        self,
        input_rgb: np.ndarray = np.zeros((FREQ_BINS, 3)),
        color: tuple[int, int, int] = (255, 255, 255),
        color_level: np.ndarray = np.array([0.5]),
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "input_rgb": {"io": "in"},
            "color_level": {"io": "in"},
            "output_rgb": {"io": "out"},
        }
        VisualPipeline.__init__(self)
        CNode.__init__(self, node_name=self.nodeName, terminals=terminals, render=render, alias=alias)

        self.input_rgb = Element(self, "input_rgb", ElementValue(input_rgb))
        self.color = ColorPicker(self, "color", ElementValue(color))
        self.color_level = LinearDial(self, "color_level", 0, 1, ElementValue(color_level))
        self.output_rgb = Element(self, "output_rgb", ElementValue(np.zeros_like(self.input_rgb.value)))

    def c_update(self):
        self.output_rgb.value[:] = np.clip(
            (self.input_rgb.value + (self.color.value * self.color_level.value) / (1 + self.color_level.value)),
            0,
            255,
        )
