import sys

from PyQt5 import QtCore, QtWidgets

from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from config import DELAY_UPDATE, FREQ_BINS, SAMPLE_RATE
from frontend.nodes.buffer import BufferNode
from frontend.nodes.features import (
    ChromaPrismNode,
    CrestFactorNode,
    EntropyNode,
    MidSideEnergyNode,
    OnsetStrengthNode,
    PitchClassChromaNode,
    SpectralCentroidNode,
    SpectralFluxNode,
    ZeroCrossingRateNode,
)
from frontend.nodes.pipelines import AmplitudesNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.stream.stream_player_node import StreamPlayerNode
from frontend.nodes.visual import BarGraphChartNode
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
        chunk_size=stream_player_node.chunk.value.shape[0],
        length=analysis_chunk_size,
        alias="analysis_buffer",
    )

    amplitudes_node = AmplitudesNode(
        buffer=buffer_node.data,
        fft_size=analysis_chunk_size,
        powering=0.28,
        normalisation=True,
        alias="amplitudes",
    )

    mid_side_node = MidSideEnergyNode(
        buffer_data=buffer_node.data,
        alias="mid_side",
    )

    zero_crossing_rate_node = ZeroCrossingRateNode(
        buffer_data=buffer_node.data,
        alias="zero_crossing_rate",
    )

    crest_factor_node = CrestFactorNode(
        buffer_data=buffer_node.data,
        alias="crest_factor",
    )

    entropy_node = EntropyNode(
        amplitudes=amplitudes_node.data,
        alias="entropy",
    )

    spectral_flux_node = SpectralFluxNode(
        amplitudes=amplitudes_node.data,
        alias="spectral_flux",
    )

    onset_strength_node = OnsetStrengthNode(
        amplitudes=amplitudes_node.data,
        alias="onset_strength",
    )

    spectral_centroid_node = SpectralCentroidNode(
        amplitudes=amplitudes_node.data,
        frequencies=amplitudes_node.frequencies,
        alias="spectral_centroid",
    )

    pitch_class_chroma_node = PitchClassChromaNode(
        amplitudes=amplitudes_node.data,
        frequencies=amplitudes_node.frequencies,
        alias="pitch_class_chroma",
    )

    chroma_prism_node = ChromaPrismNode(
        amplitudes=amplitudes_node.data,
        chroma=pitch_class_chroma_node.data,
        spectral_centroid=spectral_centroid_node.data,
        spectral_flux=spectral_flux_node.data,
        onset_strength=onset_strength_node.data,
        entropy=entropy_node.data,
        zero_crossing_rate=zero_crossing_rate_node.data,
        crest_factor=crest_factor_node.data,
        mid_side_energy=mid_side_node.data,
        alias="chroma_prism",
    )

    prism_chart_node = BarGraphChartNode(
        data=chroma_prism_node.data,
        title="Chroma Prism",
        number_points=FREQ_BINS,
        left_label="intensity",
        bottom_label="pitch / spectrum",
        brushes=chroma_prism_node.brushes,
        y_min=0,
        y_max=1,
        alias="prism_chart",
    )

    chart_window = prism_chart_node.draw()
    del chart_window

    flowchart = CFlowchart(
        terminals={
            "visual": {"io": "out"},
        },
        nodes=list(filter(lambda x: isinstance(x, CNode) and x.render, list(locals().values()))),
    )

    graph_window = QtWidgets.QMainWindow()
    graph_window.setWindowTitle("LED Node Graph - Chroma Prism")
    graph_window.setCentralWidget(flowchart.widget())
    graph_window.resize(1180, 760)
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
