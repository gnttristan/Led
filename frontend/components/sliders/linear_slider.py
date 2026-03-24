from pyqtgraph.Qt import QtWidgets

from backend.components.sliders import BLinearSlider
from frontend.components.sliders import FSlider


class FLinearSlider(QtWidgets.QWidget):
    def __init__(self, b_linear_slider: BLinearSlider):
        super().__init__()

        self.slider = FSlider(b_linear_slider)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.slider)
