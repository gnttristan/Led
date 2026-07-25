import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets, sip

from backend.updatable.updatable import VisualUpdatable
from frontend.components.elements.element_value import ElementValue
from frontend.components.elements.chart.line_chart_element import LineChartElement
from frontend.components.elements.element import Element
from frontend.components.elements.node_selector.chart_line_from_node import ChartLineNodeSelector
from frontend.components.elements.textedit.textedit import TextEdit
from frontend.overrides.CNode import CNode


class MultiLineChartElement(LineChartElement):
    def __init__(self, *args, input_data: list[float], **kwargs) -> None:
        super().__init__(*args, input_data=0.0, **kwargs)
        self.input_data = input_data
        self.data = np.zeros((len(input_data), self.number_points))
        self.lines = []
        self.legend = None

    def draw(self):
        self.node.window = pg.GraphicsLayoutWidget(title=self.title)
        plot = self.node.window.addPlot()
        self.plot = plot
        plot.setMouseEnabled(x=False, y=False)
        plot.setMenuEnabled(False)
        plot.setYRange(self.y_min, self.y_max)
        plot.setLabel("left", self.left_label)
        plot.setLabel("bottom", self.bottom_label)
        plot.showGrid(x=True, y=True)
        self.legend = pg.LegendItem(colCount=1)
        self.node.window.addItem(self.legend, row=1, col=0)
        x = np.arange(self.number_points)
        self.lines = [
            plot.plot(x, data, pen=pg.mkPen(selector.color))
            for selector, data in zip(self.node.node_selectors, self.data)
        ]
        self.line = self.lines[0] if self.lines else None
        self.update_legend()
        self.node._elements_container.layout().addWidget(self.node.window)
        return self.node.window

    def c_update(self):
        if not self.lines:
            return
        for index, value in enumerate(self.input_data):
            self.data[index] = np.roll(self.data[index], -1)
            self.data[index, -1] = value
            if not sip.isdeleted(self.lines[index]):
                self.lines[index].setPen(pg.mkPen(self.node.node_selectors[index].color))
                self.lines[index].setData(np.arange(self.number_points), self.data[index])
        self.update_legend()

    def update_legend(self):
        if self.legend is None:
            return
        self.legend.clear()
        for selector, line in zip(self.node.node_selectors, self.lines):
            element = selector.selected_element
            label = "null" if element is None else f"{element.node.name()}: {element.name}"
            self.legend.addItem(line, label)


class LineChartNode(CNode, VisualUpdatable):
    nodeName = "LineChart"

    def __init__(
        self,
        node_selectors: list[ChartLineNodeSelector] | None = None,
        title: str = "Title",
        number_points: int = 100,
        left_label: str = "Left label",
        bottom_label: str = "Bottom label",
        y_min: float = 0.0,
        y_max: float = 1.0,
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {}
        self.title = ElementValue(title)
        super().__init__(node_name=self.nodeName, terminals=terminals, render=render, alias=alias)

        self.node_selectors = node_selectors or [
            ChartLineNodeSelector(
                self,
                "node_selector",
                ElementValue(None),
                selection_nodes=self.get_flowchart_visible_nodes,
            )
        ]
        for selector in self.node_selectors:
            if selector not in self.elements:
                self.elements.append(selector)
        self.add_selector_button = QtWidgets.QPushButton("Add node selector")
        self.add_selector_button.clicked.connect(self.add_node_selector)
        self.number_points = Element(self, "number_points", ElementValue(number_points))
        self.left_label = Element(self, "left_label", ElementValue(left_label))
        self.bottom_label = Element(self, "bottom_label", ElementValue(bottom_label))
        self.y_min = TextEdit(self, "y_min", ElementValue(y_min))
        self.y_max = TextEdit(self, "y_max", ElementValue(y_max))
        self.chart = MultiLineChartElement(
            self,
            "chart",
            input_data=[0.0] * len(self.node_selectors),
            number_points=self.number_points.value,
            left_label=self.left_label.value,
            bottom_label=self.bottom_label.value,
            title=self.title.value,
            y_min=float(self.y_min.value),
            y_max=float(self.y_max.value),
            link_terminal=False,
            register_in_node=False,
        )
        self.y_min.valueChanged.connect(self.on_y_range_change)
        self.y_max.valueChanged.connect(self.on_y_range_change)

        if render:
            QtCore.QTimer.singleShot(0, self.draw)

    def init_all(self):
        super().init_all()
        self._elements_container.layout().insertWidget(len(self.node_selectors), self.add_selector_button)

    def add_node_selector(self):
        selector = ChartLineNodeSelector(
            self,
            f"node_selector_{len(self.node_selectors)}",
            ElementValue(None),
            selection_nodes=self.get_flowchart_visible_nodes,
        )
        self.node_selectors.append(selector)
        self.elements.insert(len(self.node_selectors) - 1, selector)
        self._elements_container.layout().insertWidget(len(self.node_selectors) - 1, selector)
        self.chart.input_data.append(0.0)
        self.chart.data = np.vstack((self.chart.data, np.zeros(self.chart.number_points)))
        if self.chart.lines:
            x = np.arange(self.chart.number_points)
            self.chart.lines.append(
                self.chart.plot.plot(x, self.chart.data[-1], pen=pg.mkPen(selector.color))
            )
        self.chart.update_legend()

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
        self.chart.input_data = [
            float(np.asarray(selector.selected_element.value).reshape(-1)[-1])
            if selector.selected_element is not None and np.asarray(selector.selected_element.value).size
            else 0.0
            for selector in self.node_selectors
        ]
        return self.chart.c_update()
