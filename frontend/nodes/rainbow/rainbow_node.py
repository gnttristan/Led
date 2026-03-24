from pyqtgraph.flowchart import Node

from backend.rainbow.gradient_rainbow import GradiantRainbow


class RainbowNode(Node):
    nodeName = "Rainbow"

    def __init__(self, name):
        terminals = {"rgb": {"io": "out"}}
        super().__init__(name, terminals=terminals)
        self.rainbow = GradiantRainbow()

    def process(self, display=True):
        del display
        self.rainbow.update()
        return {"rgb": self.rainbow.data.copy()}

