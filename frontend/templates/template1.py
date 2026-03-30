import sys

import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
from pyqtgraph.flowchart import Flowchart

from backend.config import DELAY_UPDATE
from frontend.nodes.pipelines.visual.rgba_pipeline import RGBAPipelineNode
from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from backend.windows_fcts.decreasing_avg_window_fct import DecreasingAvgWindowFct
from frontend.nodes.buffer import BufferNode
from frontend.nodes.pipelines import AmplitudesNode, SmoothingNode
from frontend.nodes.rainbow.gradiant_rainbow import GradiantRainbowNode
from frontend.nodes.stream import StreamNode
from frontend.nodes.visual.spectrogram_chart import SpectrogramChartNode
from frontend.registry.registry import register_nodes

register_nodes()


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
        powering=0.5,
        normalisation=True
    )
    smoothing_node = SmoothingNode(
        input_value=amplitudes_node.data,
        length=100,
        avg_axis=0,
        window_function=DecreasingAvgWindowFct
    )

    gradient_rainbow = GradiantRainbowNode()
    rgba_pipeline = RGBAPipelineNode(
        rgb=gradient_rainbow.data,
        alpha=np.ones(smoothing_node.data.value.shape[-1]) * 255
    )
    spectogram_chart_node = SpectrogramChartNode(
        data=smoothing_node.data,
        title="Amplitudes",
        number_points=smoothing_node.data.value.shape[0],
        left_label="Frequency",
        bottom_label="Amplitude",
        brushes=rgba_pipeline.rgba,
    )
    chart_window = spectogram_chart_node.draw()


    # ------------------------ ADD FLOWCHART NODES ------------------------
    # ---------------------------------------------------------------------

    flowchart = Flowchart(
        terminals={
            "amplitudes": {"io": "out"},
        }
    )
    flowchart.inputNode.graphicsItem().hide()

    flowchart.addNode(stream_node, "Stream", pos=(-400, 0))
    flowchart.addNode(buffer_node, "Buffer", pos=(0, 0))
    flowchart.addNode(amplitudes_node, "Amplitudes", pos=(400, 0))
    flowchart.addNode(smoothing_node, "Smoothing", pos=(800, 0))
    flowchart.addNode(gradient_rainbow, "GradiantRainbow", pos=(400, 400))
    flowchart.addNode(rgba_pipeline, "RGBA", pos=(800, 400))
    flowchart.addNode(spectogram_chart_node, "Window", pos=(1200, 200))



    # -------------------------- DRAW FLOWCHART ---------------------------
    # ---------------------------------------------------------------------

    graph_window = QtWidgets.QMainWindow()
    graph_window.setWindowTitle("LED Node Graph")
    graph_window.setCentralWidget(flowchart.widget())
    graph_window.resize(1100, 700)
    graph_window.show()

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
