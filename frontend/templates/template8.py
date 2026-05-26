import sys

import numpy as np
from PyQt5 import QtCore, QtWidgets

from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from config import DELAY_UPDATE, SAMPLE_RATE
from frontend.enums.gradiant.gradiant_mode import GradiantMode
from frontend.group_nodes import KickDecayNode
from frontend.nodes.broadcast.broadcast_indexes import BroadcastIndexesNode
from frontend.nodes.buffer import BufferNode
from frontend.nodes.function import FunctionNode
from frontend.nodes.pipelines import AmplitudesNode, ColorizePipelineNode
from frontend.nodes.pipelines.amplitudes.avg_frequencies import AvgFrequenciesNode
from frontend.nodes.pipelines.amplitudes.linear_amplitude_transformer_node import LinearAmplitudesTransformerNode
from frontend.nodes.pipelines.transforms.value_transformer import ValueTransformerPipelineNode
from frontend.nodes.pipelines.visual import SingleColorNode, RGBAPipelineNode, RollingNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.rainbow import GradiantNode, RainbowNode
from frontend.nodes.stream.stream_player_node import StreamPlayerNode
from frontend.nodes.visual import BarGraphChartNode
from frontend.nodes.window.window import WindowNode
from frontend.nodes.windows_fcts import DecreasingAvgWindowFct
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
        chunk_size=stream_player_node.chunk.value.shape[1],
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

    avg_frequencies_node = AvgFrequenciesNode(
        input_amplitudes=amplitudes_node.data,
        input_frequencies=amplitudes_node.frequencies,
        alias="avg_frequencies_node",
    )

    avg_frequencies_correlation_offset = ValueTransformerPipelineNode(
        input_value=avg_frequencies_node.data,
        input_value_interval=[400, 900],
        output_value_interval=[0.04, 0.12],
        alias="avg_frequencies_correlation_offset",
    )

    amplitudes_transformer_node = LinearAmplitudesTransformerNode(
        input_data=amplitudes_node.data,
        correlation_offset=avg_frequencies_correlation_offset.output_value,
        correlation_step=0.02,
        alias="amplitudes_transformer_node",
    )

    amplitudes_node_normalized = ValueTransformerPipelineNode(
        input_value=amplitudes_transformer_node.data,
        input_value_interval=[0, 7],
        output_value_interval=[0, 1],
        alias="amplitudes_node_normalized",
    )

    avg_frequencies_color_level = ValueTransformerPipelineNode(
        input_value=avg_frequencies_node.data,
        input_value_interval=[400, 900],
        output_value_interval=[0, 1],
        alias="avg_frequencies_color_level",
    )

    avg_frequencies_color_level_window = WindowNode(
        input_data=avg_frequencies_color_level.output_value,
        length=5,
        alias="avg_frequencies_color_level_window",
    )

    avg_frequencies_color_level_window_fct = DecreasingAvgWindowFct(
        window=avg_frequencies_color_level_window,
        avg_axis=0,
        alias="avg_frequencies_color_level_window_fct",
    )

    function_node = FunctionNode(
        points=[(0, 1), (0.15, 0), (0.5, 1), (0.85, 0), (1, 1)]
    )

    broadcast_indexes_node = BroadcastIndexesNode(
        input_data=amplitudes_node_normalized.output_value,
        indexes=function_node.data.value,
        alias="broadcast_node",
    )

    amplitudes_to_alpha = ValueTransformerPipelineNode(
        input_value=broadcast_indexes_node.data,
        input_value_interval=[0, 1],
        output_value_interval=[0, 255],
        alias="amplitudes_to_alpha",
    )

    rainbow_node_zero = RainbowNode(
        color_in=(255, 0, 135),
        color_out=(50, 50, 200),
        cycle=0,
        mode=GradiantMode.MIRROR,
        alias="rainbow_node_zero"
    )

    rainbow_node_one = RainbowNode(
        color_in=(200, 50, 50),
        color_out=(255, 200, 0),
        cycle=0,
        mode=GradiantMode.MIRROR,
        alias="rainbow_node_one"
    )

    rolling_rainbow_node_zero = RollingNode(
        input_data=rainbow_node_zero.data,
        roll_speed=4,
        alias="rolling_rainbow_node_zero",
    )

    rolling_rainbow_node_one = RollingNode(
        input_data=rainbow_node_one.data,
        roll_speed=-4,
        alias="rolling_rainbow_node_one",
    )

    colorize_node = ColorizePipelineNode(
        input_rgb=rolling_rainbow_node_zero.data,
        color=rolling_rainbow_node_one.data,
        color_level=avg_frequencies_color_level_window_fct.data
    )


    rgba_pipeline_node = RGBAPipelineNode(
        rgb=colorize_node.output_rgb,
        alpha=amplitudes_to_alpha.output_value,
    )

    spectogram_chart_node = BarGraphChartNode(
        data=np.ones(broadcast_indexes_node.data.value.shape[-1]),
        title="Amplitudes",
        number_points=amplitudes_node.data.value.shape[0],
        left_label="Frequency",
        bottom_label="Amplitude",
        brushes=rgba_pipeline_node.rgba,
        y_min=0,
        y_max=1,
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
