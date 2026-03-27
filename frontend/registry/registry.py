from pyqtgraph.flowchart import registerNodeType

from frontend.nodes.buffer import BufferNode
from frontend.nodes.pipelines import AmplitudesNode, SmoothingNode

nodes = [
    BufferNode,
    AmplitudesNode,
    SmoothingNode
]

def register_nodes():
    for node in nodes:
        node_registery_path = node.__module__.split(".")[2:-1]
        registerNodeType(node, [("LED", *node_registery_path)])

