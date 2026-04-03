import numpy as np
from scipy.signal import get_window

from config import FFT_SIZE, FREQ_BINS, MAX_FREQUENCY, MIN_FREQUENCY
from backend.updatable.updatable import AudioUpdatable
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.nodes.cnode import CNode

class AmplitudesNode(CNode, AudioUpdatable):
    nodeName = "Amplitudes"

    def __init__(
            self,
            buffer=np.zeros(FFT_SIZE),
            min_frequency=MIN_FREQUENCY,
            max_frequency=MAX_FREQUENCY,
            fft_size=FFT_SIZE,
            freq_bins=FREQ_BINS,
            powering=0,
            normalisation=True,
    ):
        terminals = {
            "buffer": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals)

        self.freq_bins = Element(self, "freq_bins", ElementValue(freq_bins))
        self.buffer = Element(self, "buffer", ElementValue(buffer))
        self.fft_size = Element(self, "fft_size", ElementValue(fft_size))
        self.window = get_window('hann', self.fft_size.value)
        self.min_frequency = Element(self, "min_frequency", ElementValue(min_frequency))
        self.max_frequency = Element(self, "max_frequency", ElementValue(max_frequency))
        self.frequencies = Element(
            self, "frequencies", ElementValue(np.geomspace(self.min_frequency.value, self.max_frequency.value, self.freq_bins.value))
        )
        self.bins = self.freq_to_bin(self.frequencies.value, self.fft_size.value)
        self.powering = powering
        self.data = Element(self, "data", ElementValue(np.zeros(self.freq_bins.value)))
        self.normalisation = Element(self, "normalisation", ElementValue(normalisation))

    def c_update(self):
        self.buffer_to_amplitudes()

    def buffer_to_amplitudes(self):
        windowed = self.buffer.value * self.window
        fft_result = np.fft.rfft(windowed)
        full_amplitudes = np.abs(fft_result)
        updated_amplitudes = full_amplitudes[self.bins] * np.power(self.bins.astype(np.float64), self.powering)  # ! Check

        if self.normalisation.value:
            updated_amplitudes = np.interp(
                updated_amplitudes,
                [min(updated_amplitudes), max(updated_amplitudes)],
                [0, 1]
            )

        self.data.value[:] = updated_amplitudes


    def freq_to_bin(self, frequencies, fft_size):
        return np.round(frequencies / self.max_frequency.value * (fft_size / 2)).astype(int)
