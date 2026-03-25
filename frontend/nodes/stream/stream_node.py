from backend.stream.stream import Stream
from frontend.nodes.cnode import CNode


class StreamNode(CNode):
    nodeName = "Stream"

    def __init__(self):
        super().__init__(Stream)

    def start(self):
        self.obj.start()

    def stop(self):
        self.obj.stop()
