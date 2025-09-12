import random
import numpy as np
from scipy.signal import get_window, butter, lfilter, hilbert

from Pipeline.envelop_lowfilter import EnvelopLowFilterPipeline
from Pipeline.rms import RMSPipeline
from Updatable.updatable import AudioUpdatable
from config import FREQ_BINS, MIN_FREQUENCY, MAX_FREQUENCY, SAMPLE_RATE, DELAY_UPDATE, CHUNK_SIZE
from energy.config import KICK_LOW_FREQT, KICK_HIGH_FREQT, THRESHOLD_RATIO_FREQ, MIN_HIT_INTERVAL, THRESHOLD_ENV_ENERGY, \
    THRESHOLD_ENERGY_RATIO
from window.window import Window
from windows_fcts.averaged_window_fct import AveragedWindowFct


class TempoDetector(AudioUpdatable):
    def __init__(self, spikes):
        super().__init__()
        self.buffer = buffer
        self.rms = RMSPipeline(buffer_data=buffer.data)
        self.window_rms = Window(input_data=self.rms.data, length=5000)
        self.avg_window_rms = AveragedWindowFct(self.window_rms)

        self.energy = np.zeros(1)

    def update(self):
        self.energy[:] = self.rms.data





