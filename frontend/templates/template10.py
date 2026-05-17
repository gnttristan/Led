import sys

import numpy as np
from PyQt5 import QtCore, QtWidgets
from pyqtgraph.examples.colorMapsLinearized import length

from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from config import DELAY_UPDATE, SAMPLE_RATE
from frontend.enums.gradiant.trigger_mode import TriggerMode
from frontend.group_nodes import KickDecayNode
from frontend.nodes.broadcast.broadcast_fraction import BroadcastFractionNode
from frontend.nodes.broadcast.broadcast_indexes import BroadcastIndexesNode
from frontend.nodes.broadcast.broadcast_rescaler import BroadcastRescalerNode
from frontend.nodes.buffer import BufferNode
from frontend.nodes.function import FunctionNode
from frontend.nodes.pipelines import AmplitudesNode
from frontend.nodes.pipelines.amplitudes.linear_amplitude_transformer_node import LinearAmplitudesTransformerNode
from frontend.nodes.pipelines.auditory.filter.low_filter import LowFilterPipelineNode
from frontend.nodes.pipelines.auditory.rms import RMSPipelineNode
from frontend.nodes.pipelines.transforms.value_transformer import ValueTransformerPipelineNode
from frontend.nodes.pipelines.visual import SingleColorNode, RGBAPipelineNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.rainbow import GradiantNode
from frontend.nodes.simple import ConstantArrayNode
from frontend.nodes.stream.stream_player_node import StreamPlayerNode
from frontend.nodes.trigger.trigger import TriggerNode
from frontend.nodes.visual import BarGraphChartNode
from frontend.nodes.visual.line_chart import LineChartNode
from frontend.nodes.window.window import WindowNode
from frontend.nodes.windows_fcts import AveragedWindowFct
from frontend.nodes.windows_fcts.decreasing_avg_window_fct import DecreasingAvgWindowFct
from frontend.overrides.CFlowchart import CFlowchart
from frontend.overrides.CNode import CNode
from frontend.registry.registry import register_nodes


register_nodes()


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    sc_playlist_player_node = SCPlaylistPlayer(
        cache=True,
        alias="sc_playlist_player_node"
    )

    analysis_chunk_size = int(SAMPLE_RATE * DELAY_UPDATE / 1000)

    stream_player_node = StreamPlayerNode(
        audio_in=sc_playlist_player_node.audio,
        sample_rate_in=sc_playlist_player_node.sample_rate,
        enqueue_token=sc_playlist_player_node.enqueue_token,
        chunk_size=analysis_chunk_size,
        alias="stream_player_node",
    )

    buffer_node = BufferNode(
        indata=stream_player_node.chunk,
        chunk_size=stream_player_node.chunk.value.shape[0],
        length=analysis_chunk_size,
        alias="buffer_node",
    )

    amplitudes_node = AmplitudesNode(
        buffer=buffer_node.data,
        fft_size=analysis_chunk_size,
        # powering=0.5,
        normalisation=True,
        alias="amplitudes_node",
    )

    window_node = WindowNode(
        input_data=amplitudes_node.data,
        length=3,
        alias="avg_window_node",
    )

    avg_window_node = AveragedWindowFct(
        window=window_node,
        avg_axis=0,
        alias="avg_window_node",
    )

    flowchart = CFlowchart(
        terminals={
            "kick_decay": {"io": "out"},
        },
        nodes=list(filter(lambda x: isinstance(x, CNode) and x.render, list(locals().values()))),
    )

    graph_window = QtWidgets.QMainWindow()
    graph_window.setWindowTitle("---")
    graph_window.setCentralWidget(flowchart.widget())
    graph_window.resize(1100, 700)
    graph_window.show()

    def visual_update():
        for obj in audio_updatable_objects:
            obj.c_update()
        for obj in visual_updatable_objects:
            obj.c_update()

    sc_playlist_player_node.start()

    timer = QtCore.QTimer()
    timer.timeout.connect(visual_update)
    timer.start(DELAY_UPDATE)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
