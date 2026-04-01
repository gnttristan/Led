import numpy as np

from backend.pipelines.pipeline import AudioPipeline
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.nodes.cnode import CNode


class ValueTransformerPipelineNode(CNode, AudioPipeline):
    nodeName = "ValueTransformer"

    @staticmethod
    def _compute_input_interval(values):
        min_value = float(np.min(values))
        max_value = float(np.max(values))
        if min_value == max_value:
            max_value += 1e-12
        return [min_value, max_value]

    def __init__(
            self,
            input_value,
            output_value_interval,
            input_value_interval=None,
            power=1
    ):
        terminals = {
            "input_value": {"io": "in"},
            "output_value": {"io": "out"},
        }

        super().__init__(node_name=self.nodeName, terminals=terminals)

        self.input_value = Element(self, "input_value", ElementValue(input_value))
        self.input_value_interval = (
            Element(self, "input_value_interval", ElementValue(input_value_interval)) if input_value_interval else
            Element(
                self,
                "input_value_interval",
                ElementValue(lambda: self._compute_input_interval(self.input_value.value))
            )
        )
        self.output_value_interval = Element(self, "output_value_interval", ElementValue(output_value_interval))
        self.power = Element(self, "power", ElementValue(power))
        self.output_value = Element(self, "output_value", ElementValue(np.zeros(self.input_value.value.shape[-1])))


    def c_update(self):
        self.input_value.value[:] = np.power(self.input_value.value, self.power.value)

        self.output_value.value[:] = np.interp(
            self.input_value.value,
            self.input_value_interval.value,
            self.output_value_interval.value
        )
