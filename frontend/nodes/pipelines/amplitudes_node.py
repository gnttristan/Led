from frontend.nodes.cnode import CNode

from backend.amplitudes.amplitudes import Amplitudes

class AmplitudesNode(CNode):
    nodeName = "Amplitudes"

    def __init__(self, *args, **kwargs):
        super().__init__(Amplitudes)
