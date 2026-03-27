import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
import sys
from backend.pipelines.transforms.operator_pipeline import OperatorPipeline
from backend.pipelines.visual.rgba_pipeline import RGBAPipeline
from backend.pipelines.auditory.rms import RMSPipeline
from backend.pipelines.transforms.smoothing import SmoothingPipeline
from backend.pipelines.transforms.value_transformer import ValueTransformerPipeline
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
        obj.c_update()

def visual_update():
    for obj in visual_updatable_objects:
        obj.c_update()

main_stream = Stream(callback=audio_update)

buffer = Buffer(indata=chunk_data)

amplitudes = Amplitudes(
    buffer=buffer,
    correlation_offset=0.3,
    correlation_step=0.1,
    powering=0.5,
    normalisation=True,
    log=0.7
)

smoothed_amplitudes = SmoothingPipeline(
    input_value=amplitudes.data,
    length=100,
    avg_axis=0,
)

smoothed_amplitudes_w_offset = SmoothingPipeline(
    input_value=amplitudes.data,
    length=1000,
    offset=1,
    avg_axis=0,
)

weighted_offset_pipeline = OperatorPipeline(
    operation=lambda: smoothed_amplitudes_w_offset.data * amplitudes.frequencies
)

weighted_offset_transformer = ValueTransformerPipeline(
    input_value=weighted_offset_pipeline.data,
    input_value_interval=[0, np.max(amplitudes.frequencies)],
    output_value_interval=[0, 1],
    power=1
)

baseline_pipeline = OperatorPipeline(
    operation=lambda: (
        (smoothed_amplitudes_w_offset.data * 0.5) +
        (weighted_offset_transformer.output_value * 0.5)
    )
)

smoothing_per_freq = OperatorPipeline(
    operation=lambda: np.clip(
        smoothed_amplitudes.data - (baseline_pipeline.data / 3),
        0,
        1
    )
)

# energy_bass_detector = EnergyBassDetector(
#     buffer=buffer,
# )

rms_pipeline = RMSPipeline(
    buffer_data=buffer.data
)

# outlier_frequencies_pipeline = OutlierFrequenciesPipeline(
#     input_amplitudes=smoothed_amplitudes.data - smoothed_amplitudes_w_offset.data,
#     # level_multiplier=rms_pipeline.data
# )

gradient_rainbow = GradiantRainbow()

value_transformer_pipeline = ValueTransformerPipeline(
    input_value=smoothing_per_freq.data,
    input_value_interval=[0, 1],
    output_value_interval=[0, 255],
    power=1
)

rgbp_pipeline = RGBAPipeline(
    rgb=gradient_rainbow.data,
    alpha=value_transformer_pipeline.output_value
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
timer.start(DELAY_UPDATE)  # ms

# Start Qt event loop
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
