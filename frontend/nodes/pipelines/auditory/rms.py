import numpy as np

from backend.pipelines.pipeline import AudioPipeline
from frontend.components.elements import LineChartElement
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.nodes.cnode import CNode


class RMSPipelineNode(CNode, AudioPipeline):
    nodeName = "RMS"

    def __init__(
        self,
        buffer_data: np.ndarray = np.zeros(0),
        title: str = "RMS",
        number_points: int = 100,
        left_label: str = "Level",
        bottom_label: str = "Time",
        y_min: float = 0.0,
        y_max: float = 1.0,
        render: bool = True,
    ) -> None:
        terminals = {
            "buffer_data": {"io": "in"},
            "data": {"io": "out"},
        }
        self.window = None
        super().__init__(self.nodeName, terminals, render=render)

        self.buffer_data = Element(self, "buffer_data", ElementValue(buffer_data))
        self.chart_data = Element(self, "data", ElementValue(np.zeros(number_points)))
        self.data = Element(self, "data", ElementValue(0.))
        self.title = ElementValue(title)
        self.number_points = Element(self, "number_points", ElementValue(number_points))
        self.left_label = Element(self, "left_label", ElementValue(left_label))
        self.bottom_label = Element(self, "bottom_label", ElementValue(bottom_label))
        self.y_min = Element(self, "y_min", ElementValue(y_min))
        self.y_max = Element(self, "y_max", ElementValue(y_max))
        self.line_chart = LineChartElement(
            self,
            "line_chart",
            input_data=self.chart_data.value,
            number_points=self.number_points.value,
            left_label=self.left_label.value,
            bottom_label=self.bottom_label.value,
            title=self.title.value,
            y_min=self.y_min.value,
            y_max=self.y_max.value,
            link_terminal=False,
            register_in_node=True,
        )
        self.elements.append(self.line_chart)

    def draw(self):
        return self.line_chart.draw()

    def c_update(self):
        self.data.value = float(np.sqrt(np.mean(self.buffer_data.value ** 2))) # RMS
        self.chart_data.value[:] = np.roll(self.chart_data.value, -1)
        self.chart_data.value[-1] = self.data.value
        self.line_chart.input_data = self.data.value
        return self.line_chart.c_update()
