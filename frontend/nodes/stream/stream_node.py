import numpy as np
from pyqtgraph.flowchart import Node

from config import CHUNK_SIZE
from backend.stream.stream import Stream


class StreamNode(Node):
    nodeName = "Stream"

    def __init__(self, name):
        terminals = {"chunk": {"io": "out"}}
        super().__init__(name, terminals=terminals)
        self.chunk = np.zeros(CHUNK_SIZE)
        self.stream = Stream(callback=self.audio_update)

    def audio_update(self, indata, frames, time, status):
        del frames, time, status
        self.chunk[:] = indata.flatten()

    def start(self):
        self.stream.start()

    def stop(self):
        if self.stream.sd_stream is not None:
            self.stream.sd_stream.stop()

    def process(self, display=True):
        return {"chunk": self.chunk}
