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


class EnergyBassDetector(AudioUpdatable):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

        self.rms = RMSPipeline(buffer_data=buffer.data)
        self.window_rms = Window(input_data=self.rms.data, length=2000)
        self.avg_window_rms = AveragedWindowFct(self.window_rms)

        self.energy_low_filter = EnvelopLowFilterPipeline(buffer_data=buffer.data)
        self.window_elf = Window(input_data=self.energy_low_filter.data, length=300)
        self.avg_window_elf = AveragedWindowFct(self.window_elf)

        self.current_time = 0
        self.old_kick_energy_ratio = np.zeros(1)
        self.kick_energy_ratio = np.zeros(1)

    def update(self):
        if self.avg_window_rms.data.item() == 0:
            return

        kick_energy_ratio = (self.energy_low_filter.data - self.avg_window_elf.data) / self.avg_window_rms.data

        self.kick_energy_ratio[:] = np.maximum(
            np.clip(kick_energy_ratio, 0, 1),
            self.old_kick_energy_ratio - 0.01
        )
        self.old_kick_energy_ratio[:] = self.kick_energy_ratio







