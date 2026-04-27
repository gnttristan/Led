import numpy as np

from backend.pipelines.auditory.rms import RMSPipeline
from backend.updatable.updatable import AudioUpdatable
from frontend.nodes.pipelines.auditory.low_filter import LowFilterPipelineNode
from frontend.nodes.window.window import WindowNode as Window
from frontend.nodes.windows_fcts.averaged_window_fct import AveragedWindowFct


class EnergyBassDetector(AudioUpdatable):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

        self.rms = RMSPipeline(buffer_data=buffer.data)
        self.window_rms = Window(input_data=self.rms.data, length=2000)
        self.avg_window_rms = AveragedWindowFct(self.window_rms)

        self.energy_low_filter = LowFilterPipelineNode(buffer_data=buffer.data, render=False)
        self.window_elf = Window(input_data=self.energy_low_filter.data, length=300)
        self.avg_window_elf = AveragedWindowFct(self.window_elf)

        self.current_time = 0
        self.old_kick_energy_ratio = np.zeros(1)
        self.kick_energy_ratio = np.zeros(1)

    def c_update(self):
        if self.avg_window_rms.data.item() == 0:
            return

        kick_energy_ratio = (
            self.energy_low_filter.data.value - self.avg_window_elf.data
        ) / self.avg_window_rms.data

        if np.clip(kick_energy_ratio, 0, 1) == 1:
            self.kick_energy_ratio[:] = kick_energy_ratio
        elif self.kick_energy_ratio > 0:
            self.kick_energy_ratio[:] = np.maximum(self.kick_energy_ratio - 0.001, 0)

        self.old_kick_energy_ratio[:] = self.kick_energy_ratio





