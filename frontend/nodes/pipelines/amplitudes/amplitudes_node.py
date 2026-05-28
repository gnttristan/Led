import numpy as np
from scipy.signal import get_window

from config import FFT_SIZE, FREQ_BINS, MAX_FREQUENCY, MIN_FREQUENCY, SAMPLE_RATE
from backend.updatable.updatable import AudioUpdatable
from frontend.components.elements.dials import ExpDial, LinearDial
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class AmplitudesNode(CNode, AudioUpdatable):
    nodeName = "Amplitudes"

    def __init__(
            self,
            buffer: np.ndarray = np.zeros((2, FFT_SIZE)),
            min_frequency: int | float = MIN_FREQUENCY,
            max_frequency: int | float = MAX_FREQUENCY,
            fft_size: int = FFT_SIZE,
            freq_bins: int = FREQ_BINS,
            db_floor: int | float = 5,
            db_ceil: int | float = 20,
            powering: int | float = 0.5,
            normalisation: bool = True,
            render: bool = True,
            alias: str | None = None,
    ) -> None:
        terminals = {
            "buffer": {"io": "in"},
            "frequencies": {"io": "out"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render, alias=alias)

        self.freq_bins = Element(self, "freq_bins", ElementValue(freq_bins))
        self.buffer = Element(self, "buffer", ElementValue(buffer))
        self.fft_size = Element(self, "fft_size", ElementValue(fft_size))
        self.window = get_window('hann', self.fft_size.value)
        self.min_frequency = ExpDial(self, "min_frequency", 20, 2000, ElementValue(min_frequency))
        self.max_frequency = Element(self, "max_frequency", ElementValue(max_frequency))
        self.frequencies = Element(
            self, "frequencies", ElementValue(np.geomspace(self.min_frequency.value, self.max_frequency.value, self.freq_bins.value))
        )
        # self.bins = self.freq_to_bin(self.frequencies.value, self.fft_size.value)
        self.db_floor = Element(self, "db_floor", ElementValue(db_floor))
        self.db_ceil = Element(self, "db_ceil", ElementValue(db_ceil))
        self.powering = LinearDial(self, "powering", 0, 3, ElementValue(powering))
        self.data = Element(self, "data", ElementValue(np.zeros(self.freq_bins.value)))
        self.normalisation = Element(self, "normalisation", ElementValue(normalisation))

    def c_update(self):
        self.buffer_to_amplitudes()

    def buffer_to_amplitudes(self):
        windowed = self.buffer.value * self.window
        fft_result = np.fft.rfft(windowed, n=self.fft_size.value)
        fft_frequencies = np.fft.rfftfreq(self.fft_size.value, d=1.0 / SAMPLE_RATE)
        fft_amplitudes = np.mean(np.abs(fft_result), axis=0)
        target_frequencies = self.frequencies.value
        updated_amplitudes = np.interp(
            target_frequencies,
            fft_frequencies,
            fft_amplitudes,
            left=0.0,
            right=0.0,
        )
        updated_amplitudes = updated_amplitudes * np.power(self.frequencies.value, self.powering.value)
        # updated_amplitudes = 20.0 * np.log1p(np.maximum(updated_amplitudes, 1e-12))
        # updated_amplitudes = np.maximum(updated_amplitudes + self.db_floor.value, 0)

        if self.normalisation.value:
            min_value = float(np.min(updated_amplitudes))
            max_value = float(np.max(updated_amplitudes))
            if min_value == max_value:
                updated_amplitudes = np.zeros_like(updated_amplitudes)
            else:
                updated_amplitudes = np.interp(
                    updated_amplitudes,
                    [min_value, max_value],
                    [0, 1]
                )

        self.data.value[:] = updated_amplitudes
