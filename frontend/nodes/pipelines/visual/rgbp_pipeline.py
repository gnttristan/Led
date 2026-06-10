import numpy as np

from backend.pipelines.pipeline import VisualPipeline
from config import FREQ_BINS
from frontend.components.elements.dials import LinearDial
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


POWER_LOG = 1


class RGBPPipelineNode(VisualPipeline, CNode):
    nodeName = "RGBPPipeline"

    def __init__(
        self,
        rgb: np.ndarray = np.zeros((FREQ_BINS, 3)),
        alpha: np.ndarray = np.zeros(FREQ_BINS),
        power_log: float = POWER_LOG,
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "rgb": {"io": "in"},
            "alpha": {"io": "in"},
            "output_rgb": {"io": "out"},
        }
        VisualPipeline.__init__(self)
        CNode.__init__(self, node_name=self.nodeName, terminals=terminals, render=render, alias=alias)

        self.rgb = Element(self, "rgb", ElementValue(rgb))
        self.alpha = Element(self, "alpha", ElementValue(alpha))
        self.power_log = LinearDial(self, "power_log", 0.1, 5, ElementValue(power_log))
        self.output_rgb = Element(self, "output_rgb", ElementValue(np.zeros((FREQ_BINS, 3), dtype=np.float32)))

    def c_update(self):
        rgb = self.rgb.value[:FREQ_BINS]

        self.output_rgb.value[:] = (
            rgb *
            (np.power(self.alpha.value, self.power_log.value)[:, None])
        )
