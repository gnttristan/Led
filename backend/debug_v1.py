import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
import sys
from backend.pipelines.complex.outlier_frequencies import OutlierFrequenciesPipeline
from backend.pipelines.visual.rgbp_pipeline import RGBPPipeline
from backend.pipelines.auditory.rms import RMSPipeline
from updatable.updatable import visual_updatable_objects, audio_updatable_objects
from amplitudes.amplitudes import Amplitudes
from buffer.buffer import Buffer
from config import *
from rainbow.gradient_rainbow import GradiantRainbow
from stream.stream import Stream

from visuals.spectrogram_chart import SpectrogramChart

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
    for obj in visual_updatable_objects:
        obj.update()

main_stream = Stream(callback=audio_update)

buffer = Buffer(indata=chunk_data)

amplitudes = Amplitudes(
    buffer=buffer,
    correlation_offset=0.5,
    correlation_step=0.1,
    powering=1,
    normalisation=True,
    log=0.6
)


# expanded_amplitudes = ExpandedAmplitudes(
#     amplitudes=notes_amplitudes.data,
# )

# energy_bass_detector = EnergyBassDetector(
#     buffer=buffer,
# )

rms_pipeline = RMSPipeline(
    buffer_data=buffer.data
)

outlier_frequencies_pipeline = OutlierFrequenciesPipeline(
    input_amplitudes=amplitudes.data,
    # level_multiplier=rms_pipeline.data
)

gradient_rainbow = GradiantRainbow()

rgbp_pipeline = RGBPPipeline(
    rgb=gradient_rainbow.data,
    alpha=outlier_frequencies_pipeline.alpha
)

spectrogram_chart = SpectrogramChart(
    data=outlier_frequencies_pipeline.amplitudes,
    title="Amplitudes",
    number_points=outlier_frequencies_pipeline.amplitudes.shape[0],
    left_label="Frequency",
    bottom_label="Amplitude",
    brushes=rgbp_pipeline.output_rgb
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
