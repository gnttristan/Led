from pyqtgraph.flowchart import registerNodeType

from frontend.nodes.pipelines.amplitudes.amplitude_level_function import AmplitudesLevelFunction
from frontend.nodes.pipelines.amplitudes.amplitude_transformer_node import AmplitudesTransformerNode
from frontend.nodes.pipelines.transforms.operator_node import OperatorPipelineNode
from frontend.nodes.pipelines.transforms.value_transformer import ValueTransformerPipelineNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.rainbow import GradiantRainbowNode
from frontend.nodes.buffer import BufferNode
from frontend.nodes.pipelines import AmplitudesNode, SmoothingNode
from frontend.nodes.pipelines.visual.rgba_pipeline import RGBAPipelineNode
from frontend.nodes.stream import StreamPlayerNode, StreamMicNode
from frontend.nodes.visual.spectrogram_chart import SpectrogramChartNode
from frontend.nodes.window.window import WindowNode
from frontend.nodes.windows_fcts.averaged_window_fct import AveragedWindowFct
from frontend.nodes.windows_fcts.decreasing_avg_window_fct import DecreasingAvgWindowFct

nodes = [
    BufferNode,
    AmplitudesNode,
    SmoothingNode,
    WindowNode,
    AveragedWindowFct,
    DecreasingAvgWindowFct,
    SpectrogramChartNode,
    GradiantRainbowNode,
    RGBAPipelineNode,
    ValueTransformerPipelineNode,
    OperatorPipelineNode,
    AmplitudesTransformerNode,
    AmplitudesLevelFunction,
    StreamPlayerNode,
    StreamMicNode,
    SCPlaylistPlayer
]

def register_nodes():
    for node in nodes:
        node_registery_path = node.__module__.split(".")[2:-1]
        registerNodeType(node, [("LED", *node_registery_path)])
