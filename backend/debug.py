import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
import sys
from backend.pipelines.visual.rgba_pipeline import RGBAPipeline
from backend.updatable.updatable import visual_updatable_objects, audio_updatable_objects
from backend.amplitudes.amplitudes import Amplitudes
from backend.buffer.buffer import Buffer
from config import *
from backend.rainbow.gradient_rainbow import GradiantRainbow
from backend.stream.stream import Stream

from backend.visuals.spectrogram_chart import SpectrogramChart

# crc16 = mkPredefinedCrcFun('crc-ccitt-false')
#
# seq = 0

chunk_data = np.zeros(CHUNK_SIZE)
def audio_update(indata, frames, time, status):
    global chunk_data
    chunk_data[:] = indata.flatten()

    for obj in audio_updatable_objects:
        obj.update()

def visual_update():
    global chunk_data
    for obj in visual_updatable_objects:
        obj.update()

main_stream = Stream(user_callback=audio_update)

buffer = Buffer(indata=main_stream.chunk.value)

amplitudes = Amplitudes(
    buffer=buffer.data.value,
    correlation_offset=0.3,
    correlation_step=0.1,
    powering=0.5,
    normalisation=True,
    log=0.7
)

gradient_rainbow = GradiantRainbow()

rgbp_pipeline = RGBAPipeline(
    rgb=gradient_rainbow.data,
    alpha=np.ones(amplitudes.data.value.shape[-1]) * 255
)

spectrogram_chart = SpectrogramChart(
    data=amplitudes.data.value,
    title="Amplitudes",
    number_points=amplitudes.data.value.shape[0],
    left_label="Frequency",
    bottom_label="Amplitude",
    brushes=rgbp_pipeline.rgba
)

win = spectrogram_chart.draw()

main_stream.start()


timer = QtCore.QTimer()
timer.timeout.connect(visual_update)
timer.start(DELAY_UPDATE)  # ms

# Start Qt event loop
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
