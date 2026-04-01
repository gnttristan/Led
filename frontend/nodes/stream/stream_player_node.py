import threading

import numpy as np
import sounddevice as sd

from config import CHUNK_SIZE, SAMPLE_RATE
from backend.updatable.updatable import AudioUpdatable
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.nodes.cnode import CNode


class StreamPlayerNode(CNode, AudioUpdatable):
    nodeName = "StreamPlayer"

    def __init__(self, sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE, render=True):
        terminals = {"chunk": {"io": "out"}}
        super().__init__(self.nodeName, terminals=terminals, render=render)
        self.sample_rate = Element(self, "sample_rate", ElementValue(int(sample_rate)))
        self.chunk = Element(self, "chunk", ElementValue(np.zeros(int(chunk_size), dtype=np.float32)))

        self._lock = threading.Lock()
        self._audio = np.zeros((0, 1), dtype=np.float32)
        self._song_ends = []
        self._cursor = 0
        self._stream = None
        self._running = False

    def enqueue(self, audio, sr):
        arr = np.asarray(audio, dtype=np.float32)
        arr = arr[:, None] if arr.ndim == 1 else arr
        with self._lock:
            if self._audio.shape[0] == 0:
                self.sample_rate.value = int(sr)
            elif int(sr) != int(self.sample_rate.value):
                raise ValueError("sample rate mismatch")
            if arr.shape[1] != self._audio.shape[1] and self._audio.shape[0] > 0:
                arr = arr[:, : self._audio.shape[1]]
            self._audio = np.vstack((self._audio, arr))
            self._song_ends.append(self._audio.shape[0])

    def remaining_seconds_to_song_end(self):
        with self._lock:
            for end in self._song_ends:
                if self._cursor < end:
                    return (end - self._cursor) / float(self.sample_rate.value)
        return None

    def _callback(self, outdata, frames, _time, _status):
        with self._lock:
            end = min(self._cursor + frames, self._audio.shape[0])
            take = max(0, end - self._cursor)
            outdata[:] = 0
            if take > 0:
                outdata[:take] = self._audio[self._cursor:end]
                block = outdata[:take]
                mono = block[:, 0] if block.shape[1] == 1 else np.mean(block, axis=1)
                chunk_len = self.chunk.value.shape[0]
                if mono.shape[0] < chunk_len:
                    mono = np.pad(mono, (0, chunk_len - mono.shape[0]))
                elif mono.shape[0] > chunk_len:
                    mono = mono[:chunk_len]
                self.chunk.value[:] = mono
            self._cursor = end

    def start(self):
        if self._running:
            return
        channels = 1
        with self._lock:
            if self._audio.shape[0] > 0:
                channels = self._audio.shape[1]
        self._stream = sd.OutputStream(
            callback=self._callback,
            samplerate=int(self.sample_rate.value),
            channels=channels,
            dtype="float32",
            blocksize=int(self.chunk.value.shape[0]),
        )
        self._stream.start()
        self._running = True

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._running = False

    def c_update(self):
        return self.chunk
