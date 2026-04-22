import numpy as np

from config import CHUNK_SIZE, FFT_SIZE
from backend.updatable.updatable import AudioUpdatable
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.nodes.cnode import CNode


class BufferNode(CNode, AudioUpdatable):
    nodeName = "Buffer"

    def __init__(
        self,
        indata: np.ndarray = np.zeros(CHUNK_SIZE),
        chunk_size: int = CHUNK_SIZE,
        length: int = FFT_SIZE,
        render: bool = True,
    ) -> None:
        terminals = {
            "indata": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render)

        self.indata = Element(self, "indata", ElementValue(indata))
        self.chunk_size = Element(self, "chunk_size", ElementValue(chunk_size))
        self.length = Element(self, "length", ElementValue(length))
        self.data = Element(self, "data", ElementValue(np.zeros(self.length.value)))

    def c_update(self):
        self.roll()

    def roll(self):
        chunk_size = int(self.chunk_size.value)
        self.data.value[:] = np.roll(self.data.value, -chunk_size)
        self.data.value[-chunk_size:] = self.indata.value
