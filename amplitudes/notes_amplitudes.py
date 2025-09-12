import numpy as np
from scipy.signal import get_window

from Updatable.updatable import AudioUpdatable
from config import *

OUTBOUND_LOW_INDEX = 35
OUTBOUND_HIGH_INDEX = 75

class NotesAmplitudes(AudioUpdatable):
    def __init__(
            self,
            buffer,
            outbound_low_index=OUTBOUND_LOW_INDEX,
            outbound_high_index=OUTBOUND_HIGH_INDEX,
            fft_size=FFT_SIZE,
            powering=1,
            normalisation=True,
            expand=True,
            log=None
    ):
        super().__init__()

        self.buffer = buffer
        self.fft_size = fft_size
        self.window = get_window('hann', fft_size)

        self.frequencies = self.get_notes_frequencies()
        self.max_frequency = np.max(self.frequencies)

        self.bins = self.freq_to_bin(self.frequencies, fft_size)

        self.data = np.zeros(100)

        self.normalisation = normalisation
        self.expand = expand

    def update(self):
        self.buffer_to_amplitudes()

    def buffer_to_amplitudes(self):
        print(self.bins)

        windowed = self.buffer.data * self.window
        fft_result = np.fft.rfft(windowed)
        full_amplitudes = np.abs(fft_result)
        updated_amplitudes = full_amplitudes[self.bins] * np.power(self.bins.astype(np.float64), 1.15)

        if self.normalisation:
            updated_amplitudes = np.interp(
                updated_amplitudes,
                [min(updated_amplitudes), max(updated_amplitudes)],
                [0, 1]
            )

        self.data[:] = updated_amplitudes


    def freq_to_bin(self, frequencies, fft_size):
        return np.round(frequencies / self.max_frequency * (fft_size / 2)).astype(int)

    @staticmethod
    def get_notes_frequencies():
        midi_notes = np.arange(19, 119)
        frequencies = 440.0 * 2 ** ((midi_notes - 69) / 12)
        return frequencies
