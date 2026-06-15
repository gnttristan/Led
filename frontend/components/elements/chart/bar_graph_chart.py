import numpy as np

import pyqtgraph as pg
from PyQt5 import sip

from frontend.components.elements.chart.chart_element import ChartElement


class BarGraphChartElement(ChartElement):
    def __init__(
        self,
        node,
        name: str,
        data: np.ndarray,
        number_points: int,
        left_label: str,
        bottom_label: str,
        brushes: np.ndarray,
        y_min: float,
        y_max: float,
        title: str,
        link_terminal: bool = True,
        register_in_node: bool = True,
    ) -> None:
        self.data = data
        self.number_points = number_points
        self.left_label = left_label
        self.bottom_label = bottom_label
        self.brushes = brushes
        self.y_min = y_min
        self.y_max = y_max
        self.title = title
        self.spectrogram = None
        super().__init__(node, name, link_terminal=link_terminal, register_in_node=register_in_node)

    def draw(self):
        self.node.window = pg.GraphicsLayoutWidget(title=self.title)
        plot = self.node.window.addPlot()
        plot.setYRange(self.y_min, self.y_max)
        plot.setXRange(0, self.number_points)
        plot.setLabel("left", self.left_label)
        plot.setLabel("bottom", self.bottom_label)
        plot.showGrid(x=True, y=True)
        self.spectrogram = pg.BarGraphItem(
            x=np.arange(self.number_points),
            height=np.zeros(self.number_points) + 1,
            width=1,
            brushes=self.brushes,
            pen=(0, 0, 0, 0),
        )
        plot.addItem(self.spectrogram)
        self.node.window.show()
        return self.node.window

    def c_update(self):
        if self.spectrogram is None:
            return
        if sip.isdeleted(self.spectrogram):
            self.spectrogram = None
            return
        self.spectrogram.setOpts(brushes=self.brushes, height=self.data)
