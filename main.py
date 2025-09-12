import time

import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
import sys

from Pipeline.outlier_frequencies import OutlierFrequenciesPipeline
from Pipeline.rgba_pipeline import RGBAPipeline
from Pipeline.value_transformer import ValueTransformerPipeline
from Updatable.updatable import visual_updatable_objects, audio_updatable_objects
from amplitudes.amplitudes import Amplitudes
from amplitudes.expanded_amplitudes import ExpandedAmplitudes
from amplitudes.notes_amplitudes import NotesAmplitudes
from buffer.buffer import Buffer
from config import *
from energy.energy_bass import EnergyBassDetector
from rainbow.gradient_rainbow import GradiantRainbow
from stream.stream import Stream
from visuals.line_chart import LineChart
from visuals.spectrogram_chart import SpectrogramChart

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
    powering=0.9,
    normalisation=True,
    log=0.4
)


# expanded_amplitudes = ExpandedAmplitudes(
#     amplitudes=notes_amplitudes.data,
# )

# energy_bass_detector = EnergyBassDetector(
#     buffer=buffer,
# )

outlier_frequencies_pipeline = OutlierFrequenciesPipeline(
    input_amplitudes=amplitudes.data
)

gradient_rainbow = GradiantRainbow()

rgba_pipeline = RGBAPipeline(
    rgb=gradient_rainbow.data,
    alpha=outlier_frequencies_pipeline.alpha
)

spectrogram_chart = SpectrogramChart(
    data=outlier_frequencies_pipeline.amplitudes,
    title="Amplitudes",
    number_points=outlier_frequencies_pipeline.amplitudes.shape[0],
    left_label="Frequency",
    bottom_label="Amplitude",
    brushes=rgba_pipeline.rgba
)

# line_chart = LineChart(
#     input_data=energy_bass_detector.kick_energy_ratio,
#     title="Energy Kick Ratio",
#     number_points=100,
#     left_label="Energy",
#     bottom_label="Time"
# )

win = spectrogram_chart.draw()
# win2 = line_chart.draw()

main_stream.start()


timer = QtCore.QTimer()
timer.timeout.connect(visual_update)
timer.start(DELAY_UPDATE)  # ms

# Start Qt event loop
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        time.sleep(1)
        QtWidgets.QApplication.instance().exec_()
