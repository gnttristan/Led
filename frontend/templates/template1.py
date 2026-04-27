import sys

import numpy as np
from PyQt5 import QtCore, QtWidgets

from frontend.nodes.pipelines.amplitudes.amplitude_level_function import AmplitudesLevelFunction
from config import DELAY_UPDATE
from frontend.nodes.pipelines.amplitudes.fct_amplitude_transformer_node import AmplitudesTransformerNode
from frontend.nodes.pipelines.transforms.operator_node import OperatorPipelineNode
from frontend.nodes.pipelines.transforms.value_transformer import ValueTransformerPipelineNode
from frontend.nodes.pipelines.visual.rgba_pipeline import RGBAPipelineNode
from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from frontend.nodes.buffer import BufferNode
from frontend.nodes.cnode import CNode
from frontend.nodes.pipelines import AmplitudesNode, SmoothingNode
from frontend.nodes.rainbow.gradiant_rainbow import GradiantRainbowNode
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
    buffer_node = BufferNode(indata=stream_mic_node.chunk)

    amplitudes_node = AmplitudesNode(
        buffer=buffer_node.data,
        normalisation=True
    )

    smoothing_node = SmoothingNode(
        input_value=amplitudes_node.data,
        length=130,
        avg_axis=0,
    )

    new_amplitudes_node = OperatorPipelineNode(
        arguments=[
            amplitudes_node.data,
            "-",
            smoothing_node.data
        ],
        length=smoothing_node.data.value.shape[0]
    )

    new_amplitudes_node_normalized = ValueTransformerPipelineNode(
        input_value=new_amplitudes_node.data,
        output_value_interval=[0, 1],
        power=1
    )

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
    # amplitudes_transformer_node = AmplitudesTransformerNode(
    #     input_data=amplitudes_and_smoothed_added.data,
    #     # correlation_offset=1,
    #     # correlation_step=0.5,
    #     # amplitudes_level_fct=amplitudes_level_function_node,
    #     log=0.8,
    # )
    #
    gradient_rainbow = GradiantRainbowNode()

    rgba_pipeline = RGBAPipelineNode(
        rgb=gradient_rainbow.data,
        alpha=np.ones(amplitudes_node.data.value.shape[0]) * 255
    )

    spectogram_chart_node = SpectrogramChartNode(
        data=new_amplitudes_node_normalized.output_value.value,
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
