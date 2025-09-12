import numpy as np
from scipy.signal import get_window

from config import *
from Updatable.updatable import AudioUpdatable

amplitudes = np.zeros(FREQ_BINS)

class Amplitudes(AudioUpdatable):
    def __init__(
            self,
            buffer,
            min_frequency=MIN_FREQUENCY,
            max_frequency=MAX_FREQUENCY,
            fft_size=FFT_SIZE,
            freq_bins=FREQ_BINS,
            correlation_offset=None,
            correlation_step=None,
            powering=1,
            normalisation=True,
            log=None
    ):
        super().__init__()

        self.freq_bins = freq_bins
        self.buffer = buffer
        self.fft_size = fft_size
        self.window = get_window('hann', fft_size)

        self.min_frequency = min_frequency
        self.max_frequency = max_frequency
        self.frequencies = np.geomspace(min_frequency, max_frequency, freq_bins)

        self.bins = self.freq_to_bin(self.frequencies, fft_size)

        self.data = np.zeros(freq_bins)

        self.correlation_offset = correlation_offset
        self.correlation_step = correlation_step
        self.powering = powering
        self.normalisation = normalisation
        self.log = log

    def update(self):
        self.buffer_to_amplitudes()

    def buffer_to_amplitudes(self):
        windowed = self.buffer.data * self.window
        fft_result = np.fft.rfft(windowed)
        full_amplitudes = np.abs(fft_result)
        updated_amplitudes = full_amplitudes[self.bins] * np.power(self.bins.astype(np.float64),
                                                                   self.powering)  # ! Check

        if self.log is not None:
            updated_amplitudes = np.power(updated_amplitudes, self.log)

        if self.correlation_offset is not None and self.correlation_step is not None:
            updated_amplitudes = np.correlate(
                updated_amplitudes,
                np.concatenate(
                    (
                        np.arange(1 - self.correlation_offset, 1, self.correlation_step),
                        np.arange(1, 1 - self.correlation_offset - self.correlation_step, - self.correlation_step)
                    )
                ),
                mode="same"
            )

        if self.normalisation:
            updated_amplitudes = np.interp(
                updated_amplitudes,
                [min(updated_amplitudes), max(updated_amplitudes)],
                [0, 1]
            )

        self.data[:] = updated_amplitudes

    def freq_to_bin(self, frequencies, fft_size):
        return np.round(frequencies / self.max_frequency * (fft_size / 2)).astype(int)
