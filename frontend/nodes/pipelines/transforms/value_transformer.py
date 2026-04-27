import numpy as np

from backend.pipelines.pipeline import AudioPipeline
from frontend.components.elements.dials import LinearDial
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
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

    @staticmethod
    def _compute_input_value_shape(value):
        shape_per_type = {
            float: lambda x: 1,
            int: lambda x: 1,
            np.ndarray: lambda x: x.shape[-1]
        }
        return shape_per_type[type(value)](value)

    def __init__(
            self,
            input_value: np.ndarray = np.zeros(0),
            output_value_interval: list[int | float] | tuple[int | float, int | float] = [0, 1],
            input_value_interval: list[int | float] | tuple[int | float, int | float] | None = None,
            power: float = 1,
            render: bool = True,
    ) -> None:
        terminals = {
            "input_value": {"io": "in"},
            "output_value": {"io": "out"},
        }

        super().__init__(node_name=self.nodeName, terminals=terminals, render=render)

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
        self.power = LinearDial(self, "power", 0.5, 3, ElementValue(power))
        self.output_value = Element(self, "output_value", ElementValue(
            np.zeros(self._compute_input_value_shape(self.input_value.value)))
        )


    def c_update(self):
        updated = np.power(np.maximum(self.input_value.value, 0), self.power.value)

        self.output_value.value[:] = np.interp(
            updated,
            self.input_value_interval.value,
            self.output_value_interval.value
        )
