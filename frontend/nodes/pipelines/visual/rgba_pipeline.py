import numpy as np

from backend.pipelines.pipeline import VisualPipeline
from config import FREQ_BINS
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.nodes.cnode import CNode


class RGBAPipelineNode(VisualPipeline, CNode):
    nodeName = "RGBAPipeline"

    def __init__(self, rgb, alpha):
        terminals = {
            "rgb": {"io": "in"},
            "alpha": {"io": "in"},
            "rgba": {"io": "out"},
        }
        VisualPipeline.__init__(self)
        CNode.__init__(self, node_name=self.nodeName, terminals=terminals)

        self.rgb = Element(self, "rgb", ElementValue(rgb))
        self.alpha = Element(self, "alpha", ElementValue(alpha))
        self.rgba = Element(self, "rgba", ElementValue(np.zeros((FREQ_BINS, 4))))

    def c_update(self):
        rgb = self.rgb.value[:FREQ_BINS]

        self.rgba.value[:] = np.concatenate(
            (rgb, self.alpha.value[:, np.newaxis]), axis=1
        )
