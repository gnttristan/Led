import numpy as np

from backend.pipelines.pipeline import AudioPipeline
from backend.pipelines.transforms.smoothing import SmoothingPipeline

OUTLIER_THRESHOLD = 0.3
MEAN_PER_AMP_RATIO = 0
DECREASE_RATE = 0.005
WINDOW_EFFECTIVNESS = 1

class OutlierFrequenciesPipeline(AudioPipeline):
    def __init__(
            self,
            input_amplitudes,
            outlier_threshold=OUTLIER_THRESHOLD,
            decrease_rate=DECREASE_RATE,
            mean_per_amp_ratio=MEAN_PER_AMP_RATIO,
            level_multiplier=np.ones(1)
    ):
        super().__init__()
        self.outlier_threshold = outlier_threshold
        self.decrease_rate = decrease_rate
        self.mean_per_amp_ratio = mean_per_amp_ratio
        self.level_multiplier = level_multiplier

        self.input_amplitudes = input_amplitudes
        self.amplitudes = np.zeros(self.input_amplitudes.shape[0])

        self.smoothed_amplitudes = SmoothingPipeline(
            input_value=self.input_amplitudes,
            length=500,
            avg_axis=0,
        )
        self.average_level = SmoothingPipeline(
            input_value=self.level_multiplier,
            length=3000,
        )

        self.normalized_alpha = np.zeros(self.input_amplitudes.shape[0])
        self.alpha = np.zeros(self.input_amplitudes.shape[0])


    def update(self):
        if self.average_level.data.item() == 0:
            return

        current_relative_level = self.level_multiplier / self.average_level.data

        reworked_amplitudes = self.input_amplitudes - (
                (self.smoothed_amplitudes.data * self.mean_per_amp_ratio) +
                (np.mean(self.smoothed_amplitudes.data) * (1 - self.mean_per_amp_ratio))
        ) * current_relative_level

        clipped_amplitudes = np.clip(reworked_amplitudes, 0, 1)

        current_outlier_amplitudes = np.where(
            clipped_amplitudes > self.outlier_threshold,
            1,
            0
        )

        self.normalized_alpha = np.clip(
            (self.normalized_alpha - self.decrease_rate) + current_outlier_amplitudes, 0, 1
        )

        self.amplitudes[:] = np.ceil(self.normalized_alpha)

        self.alpha[:] = self.normalized_alpha * 255
        # self.alpha[:] = np.ones(200) * 255


