import numpy as np
from config import FFT_SIZE, CHUNK_SIZE
from Updatable.updatable import AudioUpdatable


class Buffer(AudioUpdatable):
    def __init__(self, indata, fft_size=FFT_SIZE, chunk_size=CHUNK_SIZE):
        super().__init__()

        self.length = fft_size
        self.data = np.zeros(self.length)
        self.chunk_size = chunk_size
        self.indata = indata

    def update(self):
        self.roll()

    def roll(self):
        self.data[:] = np.roll(self.data, -self.chunk_size)
        self.data[-CHUNK_SIZE:] = self.indata
