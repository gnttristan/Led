from backend.updatable.updatable import VisualUpdatable
from frontend.overrides.CNode import CNode


class LineChartNode(CNode, VisualUpdatable):
    def c_update(self):
        return self.chart.c_update()
