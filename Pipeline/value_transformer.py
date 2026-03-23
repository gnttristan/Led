import numpy as np
from scipy.signal import hilbert, butter, lfilter

from Pipeline.pipeline import AudioPipeline
from config import SAMPLE_RATE
from energy.config import KICK_LOW_FREQT, KICK_HIGH_FREQT


class ValueTransformerPipeline(AudioPipeline):
    def __init__(
            self,
            input_value,
            input_value_interval,
            output_value_interval,
            power=1
    ):
        super().__init__()
        self.input_value = input_value
        self.input_value_interval = input_value_interval
        self.output_value_interval = output_value_interval
        self.power = power

        self.output_value = np.zeros(self.input_value.shape[-1])


    def update(self):
        self.input_value[:] = np.power(self.input_value, self.power)
        self.output_value[:] = np.interp(self.input_value, self.input_value_interval, self.output_value_interval)
