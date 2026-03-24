import numpy as np

from backend.updatable.updatable import AudioUpdatable


class Window(AudioUpdatable):
    def __init__(self, input_data, length, init_value=0., offset=0):
        super().__init__()
        self.length = length
        self.input_data = input_data # Data to aggregate
        self.offset = offset
        self.data = np.repeat(init_value, length * input_data.shape[0]).reshape(length, input_data.shape[0])
        self.window_fcts = []

    def update(self):
        self.roll()
        for window_fct in self.window_fcts:
            window_fct.aggregate(self.data)

    def roll(self):
        self.data[:] = np.roll(self.data, -1, axis=0)
        self.data[-1] = np.roll(self.input_data, self.offset)
