from pyqtgraph.flowchart import registerNodeType

from frontend.nodes.rainbow import GradiantRainbowNode
from frontend.nodes.buffer import BufferNode
from frontend.nodes.pipelines import AmplitudesNode, SmoothingNode
from frontend.nodes.pipelines.visual.rgba_pipeline import RGBAPipelineNode
from frontend.nodes.visual.spectrogram_chart import SpectrogramChartNode
from frontend.nodes.window.window import WindowNode

nodes = [
    BufferNode,
    AmplitudesNode,
    SmoothingNode,
    WindowNode,
    SpectrogramChartNode,
    GradiantRainbowNode,
    RGBAPipelineNode
]

def register_nodes():
    for node in nodes:
        node_registery_path = node.__module__.split(".")[2:-1]
        registerNodeType(node, [("LED", *node_registery_path)])

