import numpy as np

import pyqtgraph as pg

from backend.visuals.chart import Chart
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.nodes.cnode import CNode


class SpectrogramChartNode(Chart, CNode):
    nodeName = "Spectrogram"

    def __init__(
            self,
            data,
            title,
            number_points,
            left_label,
            bottom_label,
            brushes
    ):
        terminals = {
            "brushes": {"io": "in"},
            "data": {"io": "in"},
        }
        Chart.__init__(self, data, title)
        CNode.__init__(self, node_name=self.nodeName, terminals=terminals)

        self.number_points = Element(self, "number_points", ElementValue(number_points))
        self.brushes = Element(self, "brushes", ElementValue(brushes))
        self.left_label = Element(self, "left_label", ElementValue(left_label))
        self.bottom_label = Element(self, "bottom_label", ElementValue(bottom_label))
        self.data = Element(self, "data", ElementValue(self.data))
        self.spectrogram = None

    def draw(self):
        win = super().draw()

        plot = win.addPlot()
        plot.setYRange(0, 1)
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
            raise Exception("Chart needs to be drawed")

        super().c_update()

        self.spectrogram.setOpts(brushes=self.brushes.value, height=self.data.value)

        return self.data
