import numpy as np
from PyQt5 import QtWidgets

from frontend.components.elements.element import Element


class AnalysableElement(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._analysis_chart = None
        self.analysis_button = None
        if isinstance(self.value, np.ndarray) and self.value.ndim == 1:
            self.analysis_button = QtWidgets.QToolButton()
            self.analysis_button.setText("📈")
            self.analysis_button.setCheckable(True)
            self.analysis_button.setToolTip("Show data over time")
            self.analysis_button.toggled.connect(self._toggle_analysis_chart)
            self.container_vchange_layout.addWidget(self.analysis_button)

    def _toggle_analysis_chart(self, visible):
        if visible:
            value = np.asarray(self.value)
            if value.ndim != 1 or value.size == 0:
                self.analysis_button.setChecked(False)
                return

            from frontend.components.elements.chart.line_chart_element import LineChartElement

            self._analysis_chart = LineChartElement(
                self.node,
                f"{self.name}_chart",
                float(value[-1]),
                100,
                "Value",
                "Time",
                self.name,
                link_terminal=False,
                register_in_node=False,
            )
            self.node._elements_container.layout().insertWidget(
                self.node._elements_container.layout().indexOf(self) + 1,
                self._analysis_chart,
            )
            self.valueChanged.connect(self._update_analysis_chart)
            self._analysis_chart.draw()
        elif self._analysis_chart is not None:
            self.valueChanged.disconnect(self._update_analysis_chart)
            self._analysis_chart.setParent(None)
            self._analysis_chart.deleteLater()
            self._analysis_chart = None

    def _update_analysis_chart(self, value):
        if self._analysis_chart is None:
            return
        value = np.asarray(value).reshape(-1)
        if value.size:
            self._analysis_chart.set_input_data(float(value[-1]))
