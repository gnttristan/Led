import numpy as np

from backend.updatable.updatable import VisualUpdatable
from frontend.components.elements.element_value import ElementValue
from frontend.components.elements.line_chart_element import LineChartElement
from frontend.components.elements.element import Element
from frontend.overrides.CNode import CNode


class LineChartNode(CNode, VisualUpdatable):
    nodeName = "LineChart"

    def __init__(
        self,
        input_data: float = 0.0,
        title: str = "Title",
        number_points: int = 100,
        left_label: str = "Left label",
        bottom_label: str = "Bottom label",
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "input_data": {"io": "in"},
        }
        self.title = ElementValue(title)
        super().__init__(node_name=self.nodeName, terminals=terminals, render=render, alias=alias)

        self.input_data = Element(self, "input_data", ElementValue(input_data))
        self.number_points = Element(self, "number_points", ElementValue(number_points))
        self.left_label = Element(self, "left_label", ElementValue(left_label))
        self.bottom_label = Element(self, "bottom_label", ElementValue(bottom_label))
        self.data = Element(self, "data", ElementValue(np.zeros(number_points)))
        self.chart = LineChartElement(
            self,
            "chart",
            input_data=self.input_data.value,
            number_points=self.number_points.value,
            left_label=self.left_label.value,
            bottom_label=self.bottom_label.value,
            title=self.title.value,
            link_terminal=False,
            register_in_node=True,
        )
        self.elements.append(self.chart)

        if render:
            self.draw()
            self.chart.chart_button.setChecked(True)

    def draw(self):
        return self.chart.draw()

    def c_update(self):
        value = self.input_data.value
        if isinstance(value, np.ndarray):
            value = float(np.ravel(value)[-1]) if value.size else 0.0
        self.chart.input_data = float(value)
        return self.chart.c_update()
