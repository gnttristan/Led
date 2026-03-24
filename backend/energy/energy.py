import numpy as np

from backend.pipelines.auditory.rms import RMSPipeline
from backend.updatable.updatable import AudioUpdatable
from backend.window.window import Window
from backend.windows_fcts.averaged_window_fct import AveragedWindowFct


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





