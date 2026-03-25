import sys

import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.flowchart.library import registerNodeType

from backend.config import DELAY_UPDATE, FREQ_BINS
from backend.visuals.spectrogram_chart import SpectrogramChart
from frontend.nodes.buffer import BufferNode
from frontend.nodes.pipelines import AmplitudesNode
from frontend.nodes.stream import StreamNode

registerNodeType(BufferNode, [("LED",)])
registerNodeType(AmplitudesNode, [("LED",)])

def build_flowchart(stream_node):
    flowchart = Flowchart(
        terminals={
            "amplitudes": {"io": "out"},
        }
    )

    flowchart.addNode(stream_node, "Stream", pos=(-180, 0))
    buffer_node = flowchart.createNode("Buffer", pos=(0, 0))
    amplitudes_node = flowchart.createNode("Amplitudes", pos=(180, 0))

    flowchart.connectTerminals(stream_node["chunk"], buffer_node["indata"])
    flowchart.connectTerminals(buffer_node["data"], amplitudes_node["buffer"])
    flowchart.connectTerminals(amplitudes_node["data"], flowchart["amplitudes"])

    return flowchart


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    stream_node = StreamNode()
    flowchart = build_flowchart(stream_node)
    chart = SpectrogramChart(
        data=np.zeros(FREQ_BINS),
        title="Node Spectrogram",
        number_points=FREQ_BINS,
        left_label="Frequency",
        bottom_label="Bin",
        brushes=np.repeat([[255, 255, 255, 255]], FREQ_BINS, axis=0),
    )
    chart_window = chart.draw()

    graph_window = QtWidgets.QMainWindow()
    graph_window.setWindowTitle("LED Node Graph")
    graph_window.setCentralWidget(flowchart.widget())
    graph_window.resize(1100, 700)
    graph_window.show()

    def refresh():
        outputs = flowchart.outputValues()

        amplitudes = outputs.get("amplitudes")

        if amplitudes is not None:
            chart.data[:] = amplitudes

        chart.update()

    stream_node.start()

    timer = QtCore.QTimer()
    timer.timeout.connect(refresh)
    timer.start(DELAY_UPDATE)

    app.aboutToQuit.connect(stream_node.stop)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
