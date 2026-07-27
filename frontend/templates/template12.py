"""Aurora Pulse: a restrained, music-reactive spectrum scene."""

import sys

import numpy as np
from PyQt5 import QtCore, QtWidgets

from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from config import DELAY_UPDATE, FREQ_BINS, SAMPLE_RATE
from frontend.nodes.buffer import BufferNode
from frontend.nodes.features.entropy import EntropyNode
from frontend.nodes.features.spectral_centroid import SpectralCentroidNode
from frontend.nodes.pipelines import AmplitudesNode
from frontend.nodes.pipelines.transforms.operator_node import OperatorPipelineNode
from frontend.nodes.pipelines.visual.rgba_pipeline import RGBAPipelineNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.rainbow import GradiantNode, RainbowNode
from frontend.nodes.stream.stream_player_node import StreamPlayerNode
from frontend.nodes.visual import BarGraphChartNode, SingleLineChartNode
from frontend.overrides.CFlowchart import CFlowchart
from frontend.overrides.CNode import CNode
from frontend.registry.registry import register_nodes


register_nodes()


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    playlist = SCPlaylistPlayer(cache=True, prefetch_seconds=12, alias="aurora_playlist")
    analysis_size = int(SAMPLE_RATE * DELAY_UPDATE / 1000)

    stream = StreamPlayerNode(
        audio_in=playlist.audio,
        sample_rate_in=playlist.sample_rate,
        enqueue_token=playlist.enqueue_token,
        chunk_size=analysis_size,
        alias="aurora_stream",
    )
    buffer = BufferNode(
        indata=stream.chunk,
        chunk_size=stream.chunk.value.shape[1],
        length=analysis_size,
        alias="aurora_buffer",
    )
    amplitudes = AmplitudesNode(
        buffer=buffer.data,
        fft_size=analysis_size,
        normalisation=True,
        powering=0.25,
        alias="aurora_spectrum",
    )

    entropy = EntropyNode(amplitudes=amplitudes.data, alias="aurora_entropy")
    centroid = SpectralCentroidNode(
        amplitudes=amplitudes.data,
        frequencies=amplitudes.frequencies,
        alias="aurora_centroid",
    )

    # Entropy controls the glow while the spectrum remains the visible shape.
    glow = OperatorPipelineNode(
        arguments=[amplitudes.data, "*", entropy.data],
        length=FREQ_BINS,
        alias="aurora_glow",
    )
    gradient = GradiantNode(
        color_in=(22, 235, 214),
        color_out=(245, 52, 167),
        cycle=1.4,
        alias="aurora_gradient",
    )
    rainbow = RainbowNode(
        gradiant=gradient.data,
        inv_fraction=0.22,
        alias="aurora_rainbow",
    )
    rgba = RGBAPipelineNode(
        rgb=rainbow.data,
        alpha=glow.data,
        alias="aurora_rgba",
    )
    spectrum = BarGraphChartNode(
        data=np.ones(amplitudes.data.value.shape[-1]),
        brushes=rgba.rgba,
        title="Aurora Pulse — Live Spectrum",
        number_points=FREQ_BINS,
        left_label="energy",
        bottom_label="frequency",
        y_min=0,
        y_max=1,
        alias="aurora_spectrum_view",
    )

    entropy_chart = SingleLineChartNode(
        input_data=entropy.data,
        title="Spectral Entropy",
        left_label="entropy",
        y_min=0,
        y_max=1,
        alias="aurora_entropy_chart",
    )
    centroid_chart = SingleLineChartNode(
        input_data=centroid.data,
        title="Spectral Centroid",
        left_label="Hz",
        y_min=0,
        y_max=22000,
        alias="aurora_centroid_chart",
    )

    # Keep the glow node in the graph as a second reactive visual control.
    glow_chart = SingleLineChartNode(
        input_data=glow.data,
        title="Reactive Glow",
        left_label="level",
        y_min=0,
        y_max=1.25,
        alias="aurora_glow_chart",
    )

    flowchart = CFlowchart(
        terminals={"visual": {"io": "out"}},
        nodes=[
            node for node in (
                playlist,
                stream,
                buffer,
                amplitudes,
                entropy,
                centroid,
                glow,
                gradient,
                rainbow,
                rgba,
                spectrum,
                entropy_chart,
                centroid_chart,
                glow_chart,
            )
            if isinstance(node, CNode) and node.render
        ],
    )

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Aurora Pulse — Music Reactive Visualiser")
    window.setCentralWidget(flowchart.widget())
    window.resize(1400, 850)
    window.show()

    def update():
        for node in audio_updatable_objects:
            node.c_update()
        for node in visual_updatable_objects:
            node.c_update()

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(DELAY_UPDATE)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
