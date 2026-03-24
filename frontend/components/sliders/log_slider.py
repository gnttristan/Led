from pyqtgraph.Qt import QtWidgets

from backend.components.sliders import BLogSlider
from frontend.components.sliders import FSlider


class FLogSlider(QtWidgets.QWidget):
    def __init__(self, b_log_slider: BLogSlider):
        super().__init__()

        self.slider = FSlider(b_log_slider)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.slider)
