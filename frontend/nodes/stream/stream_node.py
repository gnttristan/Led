from backend.updatable.updatable import AudioUpdatable
from frontend.nodes.cnode import CNode
from frontend.components.sliders.linear_slider import LinearSlider

import numpy as np
import sounddevice as sd
from pyqtgraph.Qt import QtCore, QtWidgets

from backend.config import SAMPLE_RATE, CHUNK_SIZE


class StreamNode(CNode, AudioUpdatable):
    nodeName = "Stream"
    INNER_MARGIN = 8
    VALUE_RATIO = 0.2
    SLIDER_RATIO = 0.6

    def __init__(self, user_callback=None, sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE):
        self.user_callback = user_callback
        self.sample_rate = sample_rate
        self.chunk_size = LinearSlider(30, 70, value=chunk_size)
        self.chunk_size.slider.valueChanged.connect(self._on_chunk_size_changed)
        self.chunk = np.zeros(chunk_size)
        self.sd_stream = None
        self._chunk_size_proxy = None
        self._chunk_size_proxy_pending = False
        terminals = {"chunk": {"io": "out"}}
        super().__init__(self.nodeName, terminals)

    def callback(self, indata, frames, time, status):
        if self.chunk.shape != indata.flatten().shape:
            self.chunk = indata.flatten()
        else:
            self.chunk[:] = indata.flatten()
        if self.user_callback is not None:
            self.user_callback(indata, frames, time, status)

    def start(self):
        self.sd_stream = sd.InputStream(
            callback=self.callback,
            channels=1,
            samplerate=self.sample_rate,
            blocksize=int(self.chunk_size.value)
        )

        self.sd_stream.start()

    def stop(self):
        if self.sd_stream is not None:
            self.sd_stream.stop()
            self.sd_stream.close()
            self.sd_stream = None

    def _on_chunk_size_changed(self):
        new_chunk_size = int(self.chunk_size.value)
        if self.chunk.shape[0] != new_chunk_size:
            self.chunk = np.zeros(new_chunk_size)

        if self.sd_stream is not None:
            self.stop()
            self.start()

    def _attach_chunk_size_slider(self):
        self._chunk_size_proxy_pending = False
        if self._chunk_size_proxy is not None:
            return

        item = super().graphicsItem()
        chunk_terminal = self["chunk"].graphicsItem()
        terminal_label_width = int(chunk_terminal.label.boundingRect().width())
        terminal_box_width = int(chunk_terminal.box.boundingRect().width())

        control_width = 150
        value_width = int(control_width * self.VALUE_RATIO)
        slider_width = int(control_width * self.SLIDER_RATIO)

        self.chunk_size.value_label.setFixedWidth(value_width)
        self.chunk_size.slider.setFixedWidth(slider_width)
        self.chunk_size.setFixedWidth(value_width + slider_width)

        node_width = (
            self.INNER_MARGIN
            + self.chunk_size.width()
            + terminal_label_width
            + terminal_box_width
            + self.INNER_MARGIN
        )
        node_height = max(84, int(self.chunk_size.sizeHint().height()) + 42)

        item.bounds.setWidth(node_width)
        item.bounds.setHeight(node_height)
        item.setTitleOffset(56)
        item.updateTerminals()

        row_y = item.bounds.height() / 2 + 4
        if hasattr(item, "nameItem") and item.nameItem is not None:
            item.nameItem.setPos(item.bounds.width() / 2. - item.nameItem.boundingRect().width() / 2., 0)

        proxy = QtWidgets.QGraphicsProxyWidget(item)
        proxy.setWidget(self.chunk_size)
        proxy.setPos(self.INNER_MARGIN, row_y - self.chunk_size.sizeHint().height() / 2)
        self._chunk_size_proxy = proxy

        terminal_anchor_x = self.INNER_MARGIN + self.chunk_size.width() + terminal_label_width + terminal_box_width
        chunk_terminal.setAnchor(terminal_anchor_x, row_y)

    def graphicsItem(self):
        item = super().graphicsItem()
        if self._chunk_size_proxy is None and not self._chunk_size_proxy_pending:
            self._chunk_size_proxy_pending = True
            QtCore.QTimer.singleShot(0, self._attach_chunk_size_slider)
        return item

    def ctrlWidget(self):
        return None

    def c_update(self, **kwargs):
        return {"chunk": self.chunk.copy()}
