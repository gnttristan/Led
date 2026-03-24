import pyqtgraph as pg

from backend.updatable.updatable import VisualUpdatable

class Chart(VisualUpdatable):
    def __init__(self, data, title):
        super().__init__()
        self.data = data
        self.title = title
        
    def draw(self):
        win = pg.GraphicsLayoutWidget(title=self.title)
        return win

    def update(self):
        pass
