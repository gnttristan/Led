import numpy as np

from backend.pipelines.pipeline import VisualPipeline
from config import FREQ_BINS
from frontend.components.elements.color_picker import ColorPicker
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.nodes.cnode import CNode


class ColorizePipelineNode(VisualPipeline, CNode):
    nodeName = "ColorizePipeline"

    def __init__(
        self,
        input_rgb: np.ndarray = np.zeros((FREQ_BINS, 3)),
        color: tuple[int, int, int] = (255, 255, 255),
        render: bool = True,
    ) -> None:
        terminals = {
            "input_rgb": {"io": "in"},
            "color": {"io": "in"},
            "output_rgb": {"io": "out"},
        }
        VisualPipeline.__init__(self)
        CNode.__init__(self, node_name=self.nodeName, terminals=terminals, render=render)

        self.input_rgb = Element(self, "input_rgb", ElementValue(input_rgb))
        self.color = ColorPicker(self, "color", ElementValue(color))
        self.output_rgb = Element(self, "output_rgb", ElementValue(np.zeros_like(self.input_rgb.value)))

    def c_update(self):
        color_scale = np.asarray(self.color.value, dtype=float) / 255.0
        self.output_rgb.value[:] = np.clip(
            self.input_rgb.value * color_scale,
            0,
            255,
        )
