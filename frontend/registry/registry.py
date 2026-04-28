from pyqtgraph.flowchart import registerNodeType

from frontend.nodes.pipelines.amplitudes.amplitude_level_function import AmplitudesLevelFunction
from frontend.nodes.pipelines.amplitudes.linear_amplitude_transformer_node import LinearAmplitudesTransformerNode
from frontend.nodes.pipelines.amplitudes.freqscaled_amplitude_transformer_node import FreqScaledAmplitudesTransformerNode
from frontend.nodes.pipelines.amplitudes.fct_amplitude_transformer_node import FctAmplitudesTransformerNode
from frontend.nodes.pipelines.auditory.filter.band_filter import BandFilterPipelineNode
from frontend.nodes.pipelines.auditory.filter.high_filter import HighFilterPipelineNode
from frontend.nodes.pipelines.auditory.filter.low_filter import LowFilterPipelineNode
from frontend.nodes.pipelines.auditory.rms import RMSPipelineNode
from frontend.nodes.pipelines.transforms.operator_node import OperatorPipelineNode
from frontend.nodes.pipelines.transforms.value_transformer import ValueTransformerPipelineNode
from frontend.nodes.pipelines.visual import RGBAPipelineNode, RollingNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.rainbow import GradiantRainbowNode
from frontend.nodes.buffer import BufferNode
from frontend.nodes.pipelines import AmplitudesNode, SmoothingNode
from frontend.nodes.pipelines.visual.colorize_pipeline import ColorizePipelineNode
from frontend.nodes.stream import StreamPlayerNode, StreamMicNode
from frontend.nodes.visual.bar_graph_chart import BarGraphChartNode
from frontend.nodes.visual.line_chart import LineChartNode
from frontend.nodes.visual.spectrogram_chart import SpectrogramChartNode
from frontend.nodes.simple.constant_array import ConstantArrayNode
from frontend.nodes.pipelines.visual import SingleColorNode
from frontend.nodes.simple.sin_array import SinArrayNode
from frontend.nodes.window.window import WindowNode
from frontend.nodes.windows_fcts.averaged_window_fct import AveragedWindowFct
from frontend.nodes.windows_fcts.decreasing_avg_window_fct import DecreasingAvgWindowFct

nodes = [
    BufferNode,
    ConstantArrayNode,
    SingleColorNode,
    SinArrayNode,
    AmplitudesNode,
    SmoothingNode,
    LowFilterPipelineNode,
    HighFilterPipelineNode,
    BandFilterPipelineNode,
    RMSPipelineNode,
    WindowNode,
    AveragedWindowFct,
    DecreasingAvgWindowFct,
    SpectrogramChartNode,
    BarGraphChartNode,
    LineChartNode,
    GradiantRainbowNode,
    ColorizePipelineNode,
    RollingNode,
    ValueTransformerPipelineNode,
    OperatorPipelineNode,
    LinearAmplitudesTransformerNode,
    FreqScaledAmplitudesTransformerNode,
    FctAmplitudesTransformerNode,
    AmplitudesLevelFunction,
    StreamPlayerNode,
    StreamMicNode,
    SCPlaylistPlayer,
    RGBAPipelineNode,
]

def register_nodes():
    for node in nodes:
        node_registery_path = node.__module__.split(".")[2:-1]
        registerNodeType(node, [("LED", *node_registery_path)])
