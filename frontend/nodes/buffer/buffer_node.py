import numpy as np

from backend.config import CHUNK_SIZE, FFT_SIZE
from backend.updatable.updatable import AudioUpdatable
from frontend.components.element.element import Element
from frontend.nodes.cnode import CNode


class BufferNode(CNode, AudioUpdatable):
    nodeName = "Buffer"

    def __init__(self, indata=np.zeros(CHUNK_SIZE), chunk_size=CHUNK_SIZE, length=FFT_SIZE):
        terminals = {
            "indata": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals)

        self.indata = Element(self, "indata", indata)
        self.chunk_size = Element(self, "chunk_size", chunk_size)
        self.length = Element(self, "length", length)
        self.data = Element(self, "data", np.zeros(self.length.value))

    def c_update(self):
        self.roll()

    def roll(self):
        chunk_size = int(self.chunk_size.value)
        self.data.value[:] = np.roll(self.data.value, -chunk_size)
        self.data.value[-chunk_size:] = self.indata.value
