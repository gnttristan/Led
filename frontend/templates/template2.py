import sys

import numpy as np
from PyQt5 import QtCore, QtWidgets

from frontend.nodes.pipelines.amplitudes.amplitude_level_function import AmplitudesLevelFunction
from config import DELAY_UPDATE, SAMPLE_RATE
from frontend.nodes.pipelines.amplitudes.linear_amplitude_transformer_node import LinearAmplitudesTransformerNode
from frontend.nodes.pipelines.auditory.filter.low_filter import LowFilterPipelineNode
from frontend.nodes.pipelines.auditory.rms import RMSPipelineNode
from frontend.nodes.pipelines.transforms.operator_node import OperatorPipelineNode
from frontend.nodes.pipelines.transforms.value_transformer import ValueTransformerPipelineNode
from frontend.nodes.pipelines.visual import RGBAPipelineNode
from frontend.nodes.pipelines.visual.colorize_pipeline import ColorizePipelineNode
from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from frontend.nodes.buffer import BufferNode
from frontend.nodes.cnode import CNode
from frontend.nodes.pipelines import AmplitudesNode, SmoothingNode
from frontend.nodes.pipelines.visual.sliding_amp_gradient import SlidingAmpGradientNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.rainbow.gradiant_rainbow import GradiantRainbowNode
from frontend.nodes.simple import ConstantArrayNode
from frontend.nodes.stream.stream_player_node import StreamPlayerNode
from frontend.nodes.visual.spectrogram_chart import SpectrogramChartNode
from frontend.nodes.windows_fcts import DecreasingAvgWindowFct
from frontend.overrides.CFlowchart import CFlowchart
from frontend.registry.registry import register_nodes

register_nodes()

def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    sc_playlist_player_node = SCPlaylistPlayer()
    analysis_chunk_size = int(SAMPLE_RATE * DELAY_UPDATE / 1000)

    stream_player_node = StreamPlayerNode(
        audio_in=lambda: sc_playlist_player_node.audio.value,
        sample_rate_in=lambda: sc_playlist_player_node.sample_rate.value,
        enqueue_token=lambda: sc_playlist_player_node.enqueue_token.value,
        chunk_size=analysis_chunk_size,
    )

    buffer_node = BufferNode(
        indata=stream_player_node.chunk,
        chunk_size=stream_player_node.chunk.value.shape[0],
        length=analysis_chunk_size,
    )

    amplitudes_node = AmplitudesNode(
        buffer=buffer_node.data,
        fft_size=analysis_chunk_size,
        # powering=0.5,
        normalisation=True
    )
    #
    # smoothed_amplitudes_node = SmoothingNode(
    #     input_value=amplitudes_node.data,
    #     length=5,
    #     avg_axis=0,
    #     # window_function=DecreasingAvgWindowFct
    # )
    #
    # new_amplitudes_node = OperatorPipelineNode(
    #     arguments=[
    #         amplitudes_node.data,
    #         "-",
    #         smoothing_node.data
    #     ],
    #     length=smoothing_node.data.value.shape[0]
    # )
    #
    # new_amplitudes_node_normalized = ValueTransformerPipelineNode(
    #     input_value=new_amplitudes_node.data,
    #     output_value_interval=[0, 1],
    #     power=4
    # )
    #
    # amplitudes_and_smoothed_added = OperatorPipelineNode(
    #     arguments=[
    #         "(",
    #         amplitudes_node.data,
    #         "*",
    #         0.4,
    #         ")",
    #         "+",
    #         "(",
    #         new_amplitudes_node_normalized.output_value,
    #         "*",
    #         0.6,
    #         ")",
    #     ],
    #     length=new_amplitudes_node_normalized.output_value.value.shape[0]
    # )
    #
    # amplitudes_level_function_node = AmplitudesLevelFunction(
    #     number_points=amplitudes_and_smoothed_added.data.value.shape[0],
    #     render = False
    # )
    #

    low_filter_node = LowFilterPipelineNode(
        buffer_data=buffer_node.data,
    )

    rms_node = RMSPipelineNode(
        buffer_data=low_filter_node.data,
        title="RMS",
        number_points=100,
        left_label="Level",
        bottom_label="Time",
        y_min=0.0,
        y_max=1.0,
    )

    rms_transformed = ValueTransformerPipelineNode(
        input_value=rms_node.data,
        input_value_interval=[0.3, 0.5],
        output_value_interval=[0.3, 1.2],
    )

    rms_lowpass_node = RMSPipelineNode(
        buffer_data=low_filter_node.data,
        title="RMS",
        number_points=100,
        left_label="Level",
        bottom_label="Time",
        y_min=0.0,
        y_max=1.0,
    )

    rms_lowpass_transformed = ValueTransformerPipelineNode(
        input_value=rms_lowpass_node.data,
        input_value_interval=[0.2, 0.5],
        output_value_interval=[0, 1],
    )



    amplitudes_transformer_node = LinearAmplitudesTransformerNode(
        input_data=amplitudes_node.data,
        correlation_offset=0.1,
        correlation_step=0.03,
        # amplitudes_level_fct=amplitudes_level_function_node,
    )

    amplitudes_node_normalized = ValueTransformerPipelineNode(
        input_value=amplitudes_transformer_node.data,
        output_value_interval=[0, 1],
        power=0.8
    )

    amplitudes_with_rms = OperatorPipelineNode(
        arguments=[
            amplitudes_node_normalized.output_value,
            "*",
            rms_transformed.output_value,
        ],
        length=amplitudes_node_normalized.output_value.value.shape[-1],
    )

    gradient_rainbow = GradiantRainbowNode(
        inv_fraction=0.2,
        cycle=1
    )

    colorize_pipeline = ColorizePipelineNode(
        input_rgb=gradient_rainbow.data,
        color=(255, 255, 255),
    )

    amplitudes_to_alpha = ValueTransformerPipelineNode(
        input_value=amplitudes_with_rms.data,
        input_value_interval=[0, 1],
        output_value_interval=[0, 255],
    )

    rgba_pipeline = RGBAPipelineNode(
        rgb=colorize_pipeline.output_rgb,
        alpha=amplitudes_to_alpha.output_value
    )

    constant_array_one = ConstantArrayNode(
        input_value=1,
    )

    spectogram_chart_node = SpectrogramChartNode(
        data=constant_array_one.data,
        title="Amplitudes",
        number_points=amplitudes_node.data.value.shape[0],
        left_label="Frequency",
        bottom_label="Amplitude",
        brushes=rgba_pipeline.rgba,
        y_min=0,
        y_max=1,
    )

    chart_window = spectogram_chart_node.draw()

    # ------------------------ ADD FLOWCHART NODES ------------------------
    # ---------------------------------------------------------------------

    flowchart = CFlowchart(
        terminals={
            "amplitudes": {"io": "out"},
        },
        nodes=list(filter(lambda x: isinstance(x, CNode) and x.render, list(locals().values())))
    )



    # -------------------------- DRAW FLOWCHART ---------------------------
    # ---------------------------------------------------------------------

    graph_window = QtWidgets.QMainWindow()
    graph_window.setWindowTitle("LED Node Graph")
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

    app.aboutToQuit.connect(sc_playlist_player_node.stop)
    app.aboutToQuit.connect(stream_player_node.stop)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
