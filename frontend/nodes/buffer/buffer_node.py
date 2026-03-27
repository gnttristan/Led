import numpy as np

from backend.config import CHUNK_SIZE, FFT_SIZE
from backend.updatable.updatable import AudioUpdatable
from frontend.nodes.cnode import CNode


class BufferNode(CNode, AudioUpdatable):
    nodeName = "Buffer"

    def __init__(self, indata=np.zeros(CHUNK_SIZE), chunk_size=CHUNK_SIZE, length=FFT_SIZE):
        self.indata = indata
        self.chunk_size = chunk_size
        self.length = length
        self.data = np.zeros(self.length)

        terminals = {
            "indata": {"io": "in"},
            "data": {"io": "out"},
        }

        super().__init__(self.nodeName, terminals)

    def c_update(self):
        self.roll()

    def roll(self):
        chunk_size = int(self.chunk_size)
        self.data[:] = np.roll(self.data, -chunk_size)
        self.data[-CHUNK_SIZE:] = self.indata
