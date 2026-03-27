import numpy as np

from backend.pipelines.pipeline import AudioPipeline


class ValueTransformerPipeline(AudioPipeline):
    def __init__(
            self,
            input_value,
            output_value_interval,
            input_value_interval=None,
            power=1
    ):
        super().__init__()
        self.input_value = input_value
        self.input_value_interval = input_value_interval or [np.min(self.input_value), np.max(self.input_value)]
        self.output_value_interval = output_value_interval
        self.power = power

        self.output_value = np.zeros(self.input_value.shape[-1])


    def c_update(self):
        self.input_value[:] = np.power(self.input_value, self.power)
        self.output_value[:] = np.interp(self.input_value, self.input_value_interval, self.output_value_interval)
