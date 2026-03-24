from pyqtgraph.Qt import QtWidgets
from frontend.components.sliders.slider import FSlider

from backend.components.sliders import BExpSlider


class FExpSlider(QtWidgets.QWidget):
    def __init__(self, b_exp_slider: BExpSlider):
        super().__init__()

        self.slider = FSlider(b_exp_slider)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.slider)
