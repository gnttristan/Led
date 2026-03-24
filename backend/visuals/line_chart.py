import numpy as np

from backend.visuals.chart import Chart

class LineChart(Chart):
    def __init__(self, input_data, title, number_points, left_label, bottom_label):
        self.input_data = input_data
        data = np.zeros(number_points)
        super().__init__(data, title)

        self.number_points = number_points
        self.left_label = left_label
        self.bottom_label = bottom_label
        self.line = None

    def draw(self):
        win = super().draw()
        plot = win.addPlot()
        plot.setLabel('left', self.left_label)
        plot.setLabel('bottom', self.bottom_label)
        plot.showGrid(x=True, y=True)

        x = np.arange(self.number_points)

        self.line = plot.plot(x, np.zeros(self.number_points), pen='b')

        win.show()

        return win

    def update(self):
        if self.line is None:
            raise Exception("Chart needs to be drawed")

        super().update()

        x = np.arange(len(self.data))
        self.roll()

        self.line.setData(x, self.data)
        return self.data

    def roll(self):
        self.data[:] = np.roll(self.data, -1)
        self.data[-1] = self.input_data
