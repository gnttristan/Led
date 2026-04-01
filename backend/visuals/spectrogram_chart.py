import numpy as np

import pyqtgraph as pg

from backend.visuals.chart import Chart

class SpectrogramChart(Chart):
    def __init__(
            self,
            data,
            title,
            number_points,
            left_label,
            bottom_label,
            brushes
    ):
        super().__init__(data, title)

        self.number_points = number_points
        self.brushes = brushes
        self.left_label = left_label
        self.bottom_label = bottom_label
        self.spectrogram = None

    def draw(self):
        win = super().draw()

        plot = win.addPlot()
        plot.setYRange(0, 1)
        plot.setXRange(0, self.number_points)
        plot.setLabel('left', self.left_label)
        plot.setLabel('bottom', self.bottom_label)

        plot.showGrid(x=True, y=True)

        self.spectrogram = pg.BarGraphItem(
            x=np.arange(self.number_points),
            height=np.zeros(self.number_points) + 1,
            width=1,
            brushes=self.brushes,
            pen=(0, 0, 0, 0)
        )

        plot.addItem(self.spectrogram)

        win.show()

        return win

    def c_update(self):
        if self.spectrogram is None:
            raise Exception("Chart needs to be drawed")

        super().c_update()

        self.spectrogram.setOpts(brushes=self.brushes, height=self.data)

        return self.data