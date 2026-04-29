import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt5 import QtCore, QtWidgets

from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from config import DELAY_UPDATE, SAMPLE_RATE
from frontend.enums.gradiant.trigger_mode import TriggerMode
from frontend.nodes.buffer import BufferNode
from frontend.nodes.group_node import GroupNode
from frontend.nodes.pipelines.auditory.filter.low_filter import LowFilterPipelineNode
from frontend.nodes.pipelines.auditory.rms import RMSPipelineNode
from frontend.nodes.playlist_player import SCPlaylistPlayer
from frontend.nodes.stream.stream_player_node import StreamPlayerNode
from frontend.nodes.trigger.trigger import TriggerNode
from frontend.nodes.visual.line_chart import LineChartNode
from frontend.nodes.window.window import WindowNode
from frontend.nodes.windows_fcts.decreasing_avg_window_fct import DecreasingAvgWindowFct
from frontend.overrides.CFlowchart import CFlowchart
from frontend.overrides.CNode import CNode
from frontend.registry.registry import register_nodes


register_nodes()


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    analysis_chunk_size = int(SAMPLE_RATE * DELAY_UPDATE / 1000)

    sc_playlist_player_node = SCPlaylistPlayer(
        cache=True,
        render=True,
        alias="sc_playlist_player_node",
    )

    stream_player_node= StreamPlayerNode(
        audio_in=sc_playlist_player_node.audio,
        sample_rate_in=sc_playlist_player_node.sample_rate,
        enqueue_token=sc_playlist_player_node.enqueue_token,
        chunk_size=analysis_chunk_size,
        render=True,
        alias="stream_player_node",
    )

    buffer_node = BufferNode(
        indata=stream_player_node.chunk,
        chunk_size=stream_player_node.chunk.value.shape[0],
        length=analysis_chunk_size,
        render=True,
        alias="buffer_node",
    )


    kick_decay_group_node = GroupNode(
        nodes=[
            (low_filter_node := LowFilterPipelineNode(
                buffer_data=buffer_node.data,
                lowpass_freq=300,
                render=True,
                alias="low_filter_node",
            )),
            (rms_node := RMSPipelineNode(
                buffer_data=low_filter_node.data,
                render=True,
                alias="rms_node",
            )),
            (trigger_node := TriggerNode(
                input_data=rms_node.data,
                trigger_mode=TriggerMode.GREATER,
                threshold=0.35,
                render=True,
                alias="kick_trigger_node",
            )),
            (window_node := WindowNode(
                input_data=trigger_node.data,
                length=5,
                render=True,
                alias="window_node",
            )),
            (window_function := DecreasingAvgWindowFct(
                window=window_node,
                avg_axis=0,
                render=True,
                alias="window_function",
            )),
            LineChartNode(
                input_data=window_function.data,
                title="Kick Decay",
                number_points=100,
                left_label="Value",
                bottom_label="Updates",
                render=True,
                alias="kick_decay_chart_node",
            ),
        ],
        auto_start_nodes=[sc_playlist_player_node],
        title="Kick decay",
        alias="kick_decay_group_node",
    )

    chart_window = kick_decay_group_node.draw()

    flowchart = CFlowchart(
        terminals={
            "kick_decay": {"io": "out"},
        },
        nodes=list(filter(lambda x: isinstance(x, CNode) and x.render, list(locals().values()))),
    )

    graph_window = QtWidgets.QMainWindow()
    graph_window.setWindowTitle("LED Node Graph - Kick Decay Group")
    graph_window.setCentralWidget(flowchart.widget())
    graph_window.resize(1100, 700)
    graph_window.show()

    def visual_update():
        for obj in audio_updatable_objects:
            obj.c_update()
        for obj in visual_updatable_objects:
            obj.c_update()

    kick_decay_group_node.start()

    timer = QtCore.QTimer()
    timer.timeout.connect(visual_update)
    timer.start(DELAY_UPDATE)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
