import sys

import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets

from backend.config import DELAY_UPDATE
from backend.pipelines.visual.rgba_pipeline import RGBAPipeline
from backend.rainbow.gradient_rainbow import GradiantRainbow
from backend.updatable.updatable import audio_updatable_objects, visual_updatable_objects
from backend.visuals.spectrogram_chart import SpectrogramChart
from config import CHUNK_SIZE
from frontend.nodes.buffer import BufferNode
from frontend.nodes.pipelines import AmplitudesNode
from frontend.nodes.stream import StreamNode

chunk_data = np.zeros(CHUNK_SIZE)
def audio_update(indata, frames, time, status):
    global chunk_data
    chunk_data[:] = indata.flatten()

    for obj in audio_updatable_objects:
        print(amplitudes.data)
        obj.c_update()

def visual_update():
    global chunk_data
    for obj in visual_updatable_objects:
        obj.c_update()


main_stream = StreamNode(user_callback=audio_update)
buffer = BufferNode(indata=main_stream.chunk)
amplitudes = AmplitudesNode(
    buffer=buffer.data,
    correlation_offset=0.3,
    correlation_step=0.1,
    powering=0.5,
    normalisation=True,
    log=0.7
)

gradient_rainbow = GradiantRainbow()

rgbp_pipeline = RGBAPipeline(
    rgb=gradient_rainbow.data,
    alpha=np.ones(amplitudes.data.shape[-1]) * 255
)

spectrogram_chart = SpectrogramChart(
    data=amplitudes.data,
    title="Amplitudes",
    number_points=amplitudes.data.shape[0],
    left_label="Frequency",
    bottom_label="Amplitude",
    brushes=rgbp_pipeline.rgba
)

win = spectrogram_chart.draw()

main_stream.start()

timer = QtCore.QTimer()
timer.timeout.connect(visual_update)
timer.start(DELAY_UPDATE)

if __name__ == "__main__":
    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        QtWidgets.QApplication.instance().exec_()

