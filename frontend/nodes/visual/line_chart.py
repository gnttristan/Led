import numpy as np

from backend.updatable.updatable import VisualUpdatable
from frontend.components.elements.element_value import ElementValue
from frontend.components.elements.chart.line_chart_element import LineChartElement
from frontend.components.elements.element import Element
from frontend.components.elements.textedit.textedit import TextEdit
from frontend.overrides.CNode import CNode


class LineChartNode(CNode, VisualUpdatable):
    nodeName = "LineChart"

    def __init__(
        self,
        input_data: np.ndarray = np.zeros(1),
        title: str = "Title",
        number_points: int = 100,
        left_label: str = "Left label",
        bottom_label: str = "Bottom label",
        y_min: float = 0.0,
        y_max: float = 1.0,
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
        self.y_min = TextEdit(self, "y_min", ElementValue(y_min))
        self.y_max = TextEdit(self, "y_max", ElementValue(y_max))
        self.data = Element(self, "data", ElementValue(np.zeros(number_points)))
        self.chart = LineChartElement(
            self,
            "chart",
            input_data=float(self.input_data.value[-1]) if self.input_data.value.size else 0.0,
            number_points=self.number_points.value,
            left_label=self.left_label.value,
            bottom_label=self.bottom_label.value,
            title=self.title.value,
            y_min=float(self.y_min.value),
            y_max=float(self.y_max.value),
            link_terminal=False,
            register_in_node=True,
        )
        self.elements.append(self.chart)
        self.y_min.valueChanged.connect(self.on_y_range_change)
        self.y_max.valueChanged.connect(self.on_y_range_change)

        if render:
            self.draw()
            self.chart.chart_button.setChecked(True)

    def draw(self):
        return self.chart.draw()

    def on_y_range_change(self):
        try:
            self.chart.y_min = float(self.y_min.value)
            self.chart.y_max = float(self.y_max.value)
        except (TypeError, ValueError):
            return
        if self.chart.line is not None:
            self.chart.line.getViewBox().setYRange(self.chart.y_min, self.chart.y_max)

    def c_update(self):
        value = self.input_data.value
        self.chart.input_data = float(value[-1]) if value.size else 0.0
        return self.chart.c_update()
