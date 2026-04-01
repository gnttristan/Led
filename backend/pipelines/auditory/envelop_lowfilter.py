import numpy as np
from scipy.signal import hilbert, butter, lfilter

from backend.pipelines.pipeline import AudioPipeline
from config import SAMPLE_RATE
from backend.energy.config import KICK_LOW_FREQT, KICK_HIGH_FREQT


class EnvelopLowFilterPipeline(AudioPipeline):
    def __init__(self, buffer_data):
        super().__init__()
        self.buffer_data = buffer_data
        self.data = np.zeros(1)

    def c_update(self):
        filtered = self.apply_filter(self.buffer_data, SAMPLE_RATE)
        energy = np.mean(self.envelope(filtered))
        self.data[:] = energy

    def apply_filter(self, data, fs, lowcut=KICK_LOW_FREQT, highcut=KICK_HIGH_FREQT):
        b, a = self.butter_bandpass(lowcut, highcut, fs)
        return lfilter(b, a, data)

    @staticmethod
    def envelope(signal):
        analytic_signal = hilbert(signal)
        return np.abs(analytic_signal)
    
    @staticmethod
    def butter_bandpass(lowcut, highcut, fs, order=1):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        return butter(order, [low, high], btype='band')