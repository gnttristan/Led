import numpy as np
import sounddevice as sd

from backend.attributes.attribute import Attribute, AttributeType
from backend.config import SAMPLE_RATE, CHUNK_SIZE


class Stream:
    def __init__(self, user_callback, sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE):
        self.user_callback = user_callback
        self.sample_rate = Attribute(sample_rate, attr_type=AttributeType.IN)
        self.chunk_size = Attribute(chunk_size, attr_type=AttributeType.IN)
        self.chunk = Attribute(np.zeros(chunk_size), attr_type=AttributeType.OUT)
        self.sd_stream = None

    def start(self):
        self.sd_stream = sd.InputStream(
            callback=self.callback,
            channels=1,
            samplerate=self.sample_rate.value,
            blocksize=self.chunk_size.value
        )

        self.sd_stream.start()

    def callback(self, indata, frames, time, status):
        self.chunk.value[:] = indata.flatten()
        if self.user_callback is not None:
            self.user_callback(indata, frames, time, status)

    def update(self):
        pass

    def stop(self):
        if self.sd_stream is not None:
            self.sd_stream.stop()
