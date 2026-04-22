import numpy as np
from pyqtgraph.flowchart import Node

from config import FREQ_BINS


class DifferenceNode(Node):
    nodeName = "Difference"

    def __init__(self, name: str, render: bool = True) -> None:
        terminals = {
            "a": {"io": "in"},
            "b": {"io": "in"},
            "diff": {"io": "out"},
        }
        super().__init__(name, terminals=terminals)

    def c_update(self, a, b, display=True):
        del display
        if a is None:
            a = np.zeros(FREQ_BINS)
        if b is None:
            b = np.zeros(FREQ_BINS)

        return {"diff": np.clip(np.asarray(a) - np.asarray(b), 0, 1)}
