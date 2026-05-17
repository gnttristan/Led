import sys

import numpy as np
from PyQt5 import QtCore, QtWidgets

from config import DELAY_UPDATE, SAMPLE_RATE
from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from frontend.nodes.buffer import BufferNode
from frontend.nodes.external import ESP32Node
from frontend.nodes.simple import ConstantArrayNode
from frontend.overrides.CNode import CNode
from frontend.nodes.pipelines import AmplitudesNode
from frontend.nodes.pipelines.auditory.filter.low_filter import LowFilterPipelineNode
from frontend.nodes.pipelines.auditory.rms import RMSPipelineNode
from frontend.nodes.pipelines.transforms.operator_node import OperatorPipelineNode
from frontend.nodes.pipelines.transforms.value_transformer import ValueTransformerPipelineNode
from frontend.nodes.pipelines.visual import RGBAPipelineNode, RollingNode, RGBPPipelineNode
from frontend.nodes.pipelines.visual.colorize_pipeline import ColorizePipelineNode
from frontend.nodes.rainbow import RainbowNode
from frontend.nodes.stream import StreamMicNode
from frontend.nodes.visual.spectrogram_chart import SpectrogramChartNode
from frontend.overrides.CFlowchart import CFlowchart
from frontend.registry.registry import register_nodes

register_nodes()


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    def audio_update(indata, frames, time, status):
        del indata, frames, time, status
        for obj in audio_updatable_objects:
            obj.c_update()

    stream_mic_node = StreamMicNode(user_callback=audio_update)

    rainbow = RainbowNode(
        alias="rainbow",
    )

    rolling = RollingNode(
        input_data=rainbow.data,
        roll_speed=1,
        alias="rolling",
    )

    constant_array = ConstantArrayNode(
        input_value=5,
        length=rainbow.data.value.shape[0],
        alias="constant_array",
    )

    rgbp_pipeline = RGBPPipelineNode(
        rgb=rolling.data,
        alpha=constant_array.data,
        alias="rgbp_pipeline",
    )

    spectogram_chart_node = SpectrogramChartNode(
        data=np.ones(constant_array.data.value.shape[0]),
        title="Amplitudes",
        number_points=constant_array.data.value.shape[0],
        left_label="Frequency",
        bottom_label="Amplitude",
        brushes=rgbp_pipeline.output_rgb,
        y_min=0,
        y_max=1,
        alias="spectogram_chart_node",
    )

    esp32_node = ESP32Node(
        rgb=rgbp_pipeline.output_rgb,
        alias="esp32_node",
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
        for obj in visual_updatable_objects:
            obj.c_update()

    stream_mic_node.start()

    timer = QtCore.QTimer()
    timer.timeout.connect(visual_update)
    timer.start(DELAY_UPDATE)

    app.aboutToQuit.connect(stream_mic_node.stop)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
