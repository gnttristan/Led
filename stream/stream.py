import sounddevice as sd

from config import SAMPLE_RATE, CHUNK_SIZE

class Stream:
    def __init__(self, callback, sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE):
        self.callback = callback
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

    def start(self):
        sd_stream = sd.InputStream(
            callback=self.callback,
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.chunk_size
        )

        sd_stream.start()

    def callback(self, _indata, _frames, _time, _status):
        pass
