import numpy as np

from backend.attributes.attribute import Attribute, AttributeType
from backend.components.sliders.linear_slider import BLinearSlider
from backend.config import FFT_SIZE, CHUNK_SIZE
from backend.updatable.updatable import AudioUpdatable


class Buffer(AudioUpdatable):
    def __init__(self, indata=np.zeros(CHUNK_SIZE), fft_size=FFT_SIZE, chunk_size=CHUNK_SIZE):
        super().__init__()

        self.length = BLinearSlider(CHUNK_SIZE, FFT_SIZE * 4, value=fft_size, attr_type=AttributeType.IN)
        self.chunk_size = BLinearSlider(1, FFT_SIZE, value=chunk_size, attr_type=AttributeType.IN)
        self.indata = Attribute(indata, attr_type=AttributeType.IN)

        self.data = Attribute(np.zeros(fft_size), attr_type=AttributeType.OUT)


    def update(self):
        self.roll()

    def roll(self):
        chunk_size = int(self.chunk_size.value)
        self.data.value[:] = np.roll(self.data.value, -chunk_size)
        self.data.value[-CHUNK_SIZE:] = self.indata.value
