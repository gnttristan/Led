from pyqtgraph.flowchart import Node

from backend.rainbow.gradient_rainbow import GradiantRainbow


class RainbowNode(Node):
    nodeName = "Rainbow"

    def __init__(self, name):
        terminals = {"rgb": {"io": "out"}}
        super().__init__(name, terminals=terminals)
        self.rainbow = GradiantRainbow()

    def c_update(self, display=True):
        del display
        self.rainbow.c_update()
        return {"rgb": self.rainbow.data.copy()}

