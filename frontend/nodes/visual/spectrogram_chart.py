import numpy as np

import pyqtgraph as pg
from PyQt5 import sip

from backend.visuals.chart import Chart
from config import FREQ_BINS
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.nodes.cnode import CNode


class SpectrogramChartNode(Chart, CNode):
    nodeName = "Spectrogram"

    def __init__(
            self,
            data: np.ndarray = np.zeros(FREQ_BINS),
            title: str = "Title",
            number_points: int = FREQ_BINS,
            left_label: str = "Left label",
            bottom_label: str = "Bottom label",
            brushes: np.ndarray | object = np.zeros((FREQ_BINS, 4)),
            y_min: int | float = 0.0,
            y_max: int | float = 90.0,
            render: bool = True,
    ) -> None:
        terminals = {
            "brushes": {"io": "in"},
            "data": {"io": "in"},
        }
        self.spectrogram = None
        self.window = None
        Chart.__init__(self, data, title)
        CNode.__init__(self, node_name=self.nodeName, terminals=terminals, render=render)

        self.number_points = Element(self, "number_points", ElementValue(number_points))
        self.brushes = Element(self, "brushes", ElementValue(brushes))
        self.left_label = Element(self, "left_label", ElementValue(left_label))
        self.bottom_label = Element(self, "bottom_label", ElementValue(bottom_label))
        self.y_min = Element(self, "y_min", ElementValue(y_min))
        self.y_max = Element(self, "y_max", ElementValue(y_max))
        self.data = Element(self, "data", ElementValue(self.data))

        if render:
            self.draw()

    def draw(self):
        win = super().draw()
        self.window = win

        plot = win.addPlot()
        plot.setYRange(self.y_min.value, self.y_max.value)
        plot.setXRange(0, self.number_points.value)
        plot.setLabel('left', self.left_label.value)
        plot.setLabel('bottom', self.bottom_label.value)

        plot.showGrid(x=True, y=True)

        self.spectrogram = pg.BarGraphItem(
            x=np.arange(self.number_points.value),
            height=np.zeros(self.number_points.value) + 1,
            width=1,
            brushes=self.brushes.value,
            pen=(0, 0, 0, 0)
        )

        plot.addItem(self.spectrogram)

        win.show()

        return win

    def c_update(self):
        if self.spectrogram is None:
            return
            # self.draw()
            # raise Exception("Chart needs to be drawed")
        if sip.isdeleted(self.spectrogram):
            self.spectrogram = None
            return

        super().c_update()

        self.spectrogram.setOpts(brushes=self.brushes.value, height=self.data.value)

        return self.data
