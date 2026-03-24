import numpy as np

from backend.pipelines.pipeline import VisualPipeline

WHITE_LEVEL_FRACTION = 0.5

class WhiteningPipeline(VisualPipeline):
    def __init__(self, input_rgb, white_level, white_level_fraction=WHITE_LEVEL_FRACTION):
        super().__init__()
        self.input_rgb = input_rgb
        self.output_rgb = np.zeros(self.input_rgb.shape)
        self.white_level = white_level
        self.white_level_fraction = white_level_fraction

    def update(self):
        self.output_rgb[:] = np.clip(
            self.input_rgb + ((self.white_level * 255) * self.white_level_fraction),
            0,
            255
        )
