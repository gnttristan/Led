import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets

from backend.buffer.buffer import Buffer
from backend.config import CHUNK_SIZE, FFT_SIZE
from frontend.nodes.cnode import CNode


class BufferNode(CNode):
    nodeName = "Buffer"

    def __init__(self, *args, **kwargs):
        super().__init__(Buffer)
