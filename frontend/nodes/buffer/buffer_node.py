import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets

from backend.buffer.buffer import Buffer
from backend.config import CHUNK_SIZE, FFT_SIZE
from frontend.nodes.cnode import CNode


class BufferNode(CNode):
    nodeName = "Buffer"

    def __init__(self, *args, **kwargs):
        super().__init__(Buffer)
        self.chunk = np.zeros(CHUNK_SIZE)
        self.buffer_source = self.chunk.copy()
        self.buffer = Buffer(indata=self.buffer_source, fft_size=FFT_SIZE, chunk_size=CHUNK_SIZE)
