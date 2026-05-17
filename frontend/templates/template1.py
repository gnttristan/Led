import sys

from PyQt5 import QtCore, QtWidgets

from config import DELAY_UPDATE, SAMPLE_RATE
from frontend.enums.gradiant.gradiant_mode import GradiantMode
from frontend.group_nodes import KickDecayNode
from frontend.nodes.features import CrestFactorNode, OnsetStrengthNode
from frontend.nodes.function.outbounds_fct import OutboundsFctNode
from frontend.nodes.pipelines.amplitudes.freqscaled_amplitude_transformer_node import \
    FreqScaledAmplitudesTransformerNode
from frontend.nodes.pipelines.amplitudes.linear_amplitude_transformer_node import LinearAmplitudesTransformerNode
from frontend.nodes.pipelines.auditory.filter.low_filter import LowFilterPipelineNode
from frontend.nodes.pipelines.auditory.rms import RMSPipelineNode
from frontend.nodes.pipelines.transforms.operator_node import OperatorPipelineNode
from frontend.nodes.pipelines.transforms.smoothing_node import SmoothingNode
from frontend.nodes.pipelines.transforms.value_transformer import ValueTransformerPipelineNode
from frontend.nodes.pipelines.visual import RGBAPipelineNode, SingleColorNode, RollingNode
from frontend.nodes.pipelines.visual.colorize_pipeline import ColorizePipelineNode
from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from frontend.nodes.buffer import BufferNode
from frontend.nodes.visual import BarGraphChartNode
from frontend.overrides.CNode import CNode
from frontend.nodes.pipelines import AmplitudesNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.rainbow import RainbowNode
from frontend.nodes.simple import ConstantArrayNode, SinArrayNode
from frontend.nodes.stream.stream_player_node import StreamPlayerNode
from frontend.nodes.visual.spectrogram_chart import SpectrogramChartNode
from frontend.overrides.CFlowchart import CFlowchart
from frontend.registry.registry import register_nodes

register_nodes()

def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    sc_playlist_player_node = SCPlaylistPlayer(alias="sc_playlist_player_node")
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

    sin_array_node = SinArrayNode(
        alias="sin_array_node",
        center=0.3,
        offset=0.1
    )

    rolling_sin = RollingNode(
        input_data=sin_array_node.data,
        roll_speed=2,
        alias="rolling_sin",
    )

    gradiant_rainbow = RainbowNode(
        color_in=(0, 0, 255),
        color_out=(127, 0, 127),
        cycle=-0.05,
        mode=GradiantMode.MIRROR,
        alias="gradiant_rainbow",
    )

    rolling_rgb = RollingNode(
        input_data=gradiant_rainbow.data,
        roll_speed=3,
        alias="rolling_brushes",
    )

    kick_decay_node = KickDecayNode(
        buffer_data=buffer_node.data,
        lowpass_freq=300,
        threshold=0.3,
        decay_length=5,
        alias="kick_decay_node",
    )

    outbounds_up_fct = OutboundsFctNode(
        y_outbound=kick_decay_node.data,
        alias="outbounds_up_fct",
    )

    alpha_with_outbound_up = OperatorPipelineNode(
        arguments=[
            rolling_sin.data,
            "+",
            outbounds_up_fct.data,
        ],
        length=outbounds_up_fct.data.value.shape[-1],
        alias="alpha_with_outbound_up",
    )

    sin_to_alpha = ValueTransformerPipelineNode(
        input_value=alpha_with_outbound_up.data,
        input_value_interval=[0, 1.5],
        output_value_interval=[0, 255],
        alias="sin_to_alpha",
    )

    rgba_pipeline = RGBAPipelineNode(
        rgb=rolling_rgb.data,
        alpha=sin_to_alpha.output_value,
    )

    constant_array_one = ConstantArrayNode(
        input_value=1,
        alias="constant_array_one",
    )

    bar_graph_chart_node = BarGraphChartNode(
        data=constant_array_one.data,
        title="Amplitudes",
        number_points=sin_array_node.data.value.shape[0],
        left_label="Frequency",
        bottom_label="Amplitude",
        brushes=rgba_pipeline.rgba,
        y_min=0,
        y_max=1,
    )

    chart_window = bar_graph_chart_node.draw()

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

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
