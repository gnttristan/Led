import sys

from PyQt5 import QtCore, QtWidgets

from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from config import DELAY_UPDATE, FREQ_BINS, SAMPLE_RATE
from frontend.nodes.buffer import BufferNode
from frontend.nodes.features import (
    EntropyNode,
    OnsetStrengthNode,
    SpectralCentroidNode,
    SpectralFluxNode,
)
from frontend.nodes.pipelines import AmplitudesNode
from frontend.nodes.pipelines.amplitudes.linear_amplitude_transformer_node import LinearAmplitudesTransformerNode
from frontend.nodes.pipelines.transforms.operator_node import OperatorPipelineNode
from frontend.nodes.pipelines.transforms.value_transformer import ValueTransformerPipelineNode
from frontend.nodes.pipelines.visual import RGBAPipelineNode, RollingNode
from frontend.nodes.broadcast.broadcast_addition import BroadcastAdditionNode
from frontend.nodes.pipelines.visual.sliding_amp_gradient import SlidingAmpGradientNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.simple import SinArrayNode
from frontend.nodes.stream.stream_player_node import StreamPlayerNode
from frontend.nodes.visual import BarGraphChartNode
from frontend.nodes.window.window import WindowNode
from frontend.nodes.windows_fcts.decreasing_avg_window_fct import DecreasingAvgWindowFct
from frontend.overrides.CFlowchart import CFlowchart
from frontend.overrides.CNode import CNode
from frontend.registry.registry import register_nodes

register_nodes()


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    sc_playlist_player_node = SCPlaylistPlayer(
        cache=True,
        prefetch_seconds=20,
        alias="soundcloud_playlist",
    )
    analysis_chunk_size = int(SAMPLE_RATE * DELAY_UPDATE / 1000)

    stream_player_node = StreamPlayerNode(
        audio_in=sc_playlist_player_node.audio,
        sample_rate_in=sc_playlist_player_node.sample_rate,
        enqueue_token=sc_playlist_player_node.enqueue_token,
        chunk_size=analysis_chunk_size,
        alias="stream_player",
    )

    buffer_node = BufferNode(
        indata=stream_player_node.chunk,
        chunk_size=stream_player_node.chunk.value.shape[1],
        length=analysis_chunk_size,
        alias="analysis_buffer",
    )

    # ------------------------------------------------------------------
    # Audio analysis
    # ------------------------------------------------------------------

    amplitudes_node = AmplitudesNode(
        buffer=buffer_node.data,
        fft_size=analysis_chunk_size,
        powering=0.25,
        normalisation=True,
        alias="amplitudes",
    )

    transformed_amplitudes = LinearAmplitudesTransformerNode(
        input_data=amplitudes_node.data,
        correlation_offset=0.1,
        correlation_step=0.03,
        log=0.4,
        alias="transformed_amplitudes",
    )

    # ------------------------------------------------------------------
    # Feature extractors
    # ------------------------------------------------------------------

    onset_strength_node = OnsetStrengthNode(
        amplitudes=amplitudes_node.data,
        alias="onset_strength",
    )

    spectral_flux_node = SpectralFluxNode(
        amplitudes=amplitudes_node.data,
        alias="spectral_flux",
    )

    entropy_node = EntropyNode(
        amplitudes=amplitudes_node.data,
        alias="entropy",
    )

    spectral_centroid_node = SpectralCentroidNode(
        amplitudes=amplitudes_node.data,
        frequencies=amplitudes_node.frequencies,
        alias="spectral_centroid",
    )

    # ------------------------------------------------------------------
    # Fluid heights via smoothed amplitudes
    # ------------------------------------------------------------------

    amplitudes_window = WindowNode(
        input_data=transformed_amplitudes.data,
        length=15,
        alias="amplitudes_window",
    )

    amplitudes_window_fct = DecreasingAvgWindowFct(
        window=amplitudes_window,
        avg_axis=0,
        alias="amplitudes_window_fct",
    )

    fluid_heights = ValueTransformerPipelineNode(
        input_value=amplitudes_window_fct.data,
        input_value_interval=[0, 2.5],
        output_value_interval=[0, 1],
        alias="fluid_heights",
    )

    # ------------------------------------------------------------------
    # Color generation — nebula gradient shifts with spectral content
    # ------------------------------------------------------------------

    nebula_gradient = SlidingAmpGradientNode(
        input_frequencies=amplitudes_node.frequencies,
        input_amplitudes=amplitudes_node.data,
        slide_window_fraction=0.12,
        slide_min_avg_amp=600,
        slide_max_avg_amp=3200,
        alias="nebula_gradient",
    )

    # Tint toward hot pink when the spectrum is treble-heavy
    centroid_color_level = ValueTransformerPipelineNode(
        input_value=spectral_centroid_node.data,
        input_value_interval=[500, 4000],
        output_value_interval=[0, 0.5],
        alias="centroid_color_level",
    )

    colorized_nebula = BroadcastAdditionNode(
        input_data=nebula_gradient.data,
        secondary_data=(255, 40, 180),
        level=centroid_color_level.output_value,
        alias="colorized_nebula",
    )

    # ------------------------------------------------------------------
    # Breathing wave for organic alpha pulsing
    # ------------------------------------------------------------------

    breath_wave = SinArrayNode(
        number_cycle=1.5,
        center=0.25,
        offset=0.12,
        alias="breath_wave",
    )

    rolling_breath = RollingNode(
        input_data=breath_wave.data,
        roll_speed=1,
        alias="rolling_breath",
    )

    breath_mod = ValueTransformerPipelineNode(
        input_value=rolling_breath.data,
        input_value_interval=[0, 0.5],
        output_value_interval=[0.5, 1.3],
        alias="breath_mod",
    )

    # ------------------------------------------------------------------
    # Alpha composition — multi-layered reactivity
    # ------------------------------------------------------------------

    onset_alpha = ValueTransformerPipelineNode(
        input_value=onset_strength_node.data,
        input_value_interval=[0, 0.25],
        output_value_interval=[0, 100],
        alias="onset_alpha",
    )

    flux_alpha = ValueTransformerPipelineNode(
        input_value=spectral_flux_node.data,
        input_value_interval=[0, 0.2],
        output_value_interval=[0, 60],
        alias="flux_alpha",
    )

    entropy_alpha = ValueTransformerPipelineNode(
        input_value=entropy_node.data,
        input_value_interval=[0, 1],
        output_value_interval=[20, 80],
        alias="entropy_alpha",
    )

    base_alpha = OperatorPipelineNode(
        arguments=[
            fluid_heights.output_value,
            "*",
            170,
            "*",
            breath_mod.output_value,
        ],
        length=FREQ_BINS,
        alias="base_alpha",
    )

    combined_alpha = OperatorPipelineNode(
        arguments=[
            base_alpha.data,
            "+",
            onset_alpha.output_value,
            "+",
            flux_alpha.output_value,
            "+",
            entropy_alpha.output_value,
        ],
        length=FREQ_BINS,
        alias="combined_alpha",
    )

    capped_alpha = ValueTransformerPipelineNode(
        input_value=combined_alpha.data,
        input_value_interval=[0, 400],
        output_value_interval=[0, 1],
        alias="capped_alpha",
    )

    rgba_pipeline = RGBAPipelineNode(
        rgb=colorized_nebula.data,
        alpha=capped_alpha.output_value,
        alias="rgba_pipeline",
    )

    # ------------------------------------------------------------------
    # Output chart — real heights meet dynamic RGBA brushes
    # ------------------------------------------------------------------

    nebula_chart = BarGraphChartNode(
        data=fluid_heights.output_value,
        title="Nebula Drift",
        number_points=FREQ_BINS,
        left_label="intensity",
        bottom_label="spectrum",
        brushes=rgba_pipeline.rgba,
        y_min=0,
        y_max=1,
        alias="nebula_chart",
    )

    chart_window = nebula_chart.draw()
    del chart_window

    # ------------------------------------------------------------------
    # Flowchart
    # ------------------------------------------------------------------

    flowchart = CFlowchart(
        terminals={
            "visual": {"io": "out"},
        },
        nodes=list(filter(lambda x: isinstance(x, CNode) and x.render, list(locals().values()))),
    )

    graph_window = QtWidgets.QMainWindow()
    graph_window.setWindowTitle("LED Node Graph - Nebula Drift")
    graph_window.setCentralWidget(flowchart.widget())
    graph_window.resize(1200, 800)
    graph_window.show()

    # ------------------------------------------------------------------
    # Update loop
    # ------------------------------------------------------------------

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
