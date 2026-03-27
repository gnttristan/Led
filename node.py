import sys

import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
from pyqtgraph.flowchart import Flowchart, registerNodeType

from backend.config import DELAY_UPDATE
from backend.pipelines.visual.rgba_pipeline import RGBAPipeline
from backend.rainbow.gradient_rainbow import GradiantRainbow
from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from backend.visuals.spectrogram_chart import SpectrogramChart
from frontend.nodes.buffer import BufferNode
from frontend.nodes.pipelines import AmplitudesNode
from frontend.nodes.stream import StreamNode
from frontend.registry.registry import register_nodes

register_nodes()

def build_flowchart(stream_node, buffer_node, amplitudes_node):
    flowchart = Flowchart(
        terminals={
            "amplitudes": {"io": "out"},
        }
    )

    flowchart.addNode(stream_node, "Stream", pos=(-180, 0))
    flowchart.addNode(buffer_node, "Buffer", pos=(0, 0))
    flowchart.addNode(amplitudes_node, "Amplitudes", pos=(180, 0))

    return flowchart


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    def audio_update(indata, frames, time, status):
        del indata, frames, time, status
        for obj in audio_updatable_objects:
            obj.c_update()

    stream_node = StreamNode(user_callback=audio_update)
    buffer_node = BufferNode(indata=stream_node.chunk)
    amplitudes_node = AmplitudesNode(
        buffer=buffer_node.data,
        correlation_offset=0.3,
        correlation_step=0.1,
        powering=0.5,
        normalisation=True,
        log=0.7
    )
    flowchart = build_flowchart(stream_node, buffer_node, amplitudes_node)

    gradient_rainbow = GradiantRainbow()
    rgbp_pipeline = RGBAPipeline(
        rgb=gradient_rainbow.data,
        alpha=np.ones(amplitudes_node.data.shape[-1]) * 255
    )
    chart = SpectrogramChart(
        data=amplitudes_node.data,
        title="Amplitudes",
        number_points=amplitudes_node.data.shape[0],
        left_label="Frequency",
        bottom_label="Amplitude",
        brushes=rgbp_pipeline.rgba,
    )
    chart_window = chart.draw()

    graph_window = QtWidgets.QMainWindow()
    graph_window.setWindowTitle("LED Node Graph")
    graph_window.setCentralWidget(flowchart.widget())
    graph_window.resize(1100, 700)
    graph_window.show()

    def connect_graph():
        flowchart.connectTerminals(stream_node["chunk"], buffer_node["indata"])
        flowchart.connectTerminals(buffer_node["data"], amplitudes_node["buffer"])
        flowchart.connectTerminals(amplitudes_node["data"], flowchart["amplitudes"])

    QtCore.QTimer.singleShot(0, connect_graph)

    def visual_update():
        for obj in visual_updatable_objects:
            obj.c_update()

    stream_node.start()

    timer = QtCore.QTimer()
    timer.timeout.connect(visual_update)
    timer.start(DELAY_UPDATE)

    app.aboutToQuit.connect(stream_node.stop)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
