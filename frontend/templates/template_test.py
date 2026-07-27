import sys

import numpy as np
from PyQt5 import QtCore, QtWidgets

from backend.updatable.updatable import visual_updatable_objects
from config import DELAY_UPDATE, FREQ_BINS
from frontend.nodes.controllers import ESP32Node
from frontend.nodes.pipelines.visual import RGBAPipelineNode, SingleColorNode
from frontend.nodes.simple import ConstantArrayNode
from frontend.nodes.visual import BarGraphChartNode
from frontend.overrides.CFlowchart import CFlowchart
from frontend.overrides.CNode import CNode
from frontend.registry.registry import register_nodes


register_nodes()


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    white = SingleColorNode(
        color=(255, 255, 255),
        number_points=FREQ_BINS,
        alias="white",
    )
    alpha = ConstantArrayNode(
        input_value=10 / 255.,
        length=FREQ_BINS,
        alias="alpha",
    )
    rgba = RGBAPipelineNode(
        rgb=white.data,
        alpha=alpha.data,
        alias="rgba",
    )
    chart = BarGraphChartNode(
        data=alpha.data,
        title="White test (alpha = 1)",
        number_points=FREQ_BINS,
        left_label="Alpha",
        bottom_label="LED",
        brushes=rgba.rgba,
        y_min=0,
        y_max=1,
        alias="chart",
    )
    esp32 = ESP32Node(
        rgba=rgba.rgba,
    )

    flowchart = CFlowchart(
        terminals={},
        nodes=[node for node in (white, alpha, rgba, chart, esp32) if isinstance(node, CNode)],
    )
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("ESP32 white test")
    window.setCentralWidget(flowchart.widget())
    window.resize(1100, 700)
    window.show()

    def visual_update():
        for obj in visual_updatable_objects:
            obj.c_update()

    timer = QtCore.QTimer()
    timer.timeout.connect(visual_update)
    timer.start(DELAY_UPDATE)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
