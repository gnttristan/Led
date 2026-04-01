import os
import tempfile
import threading
import time

import numpy as np
import soundfile as sf
from yt_dlp import YoutubeDL

from backend.updatable.updatable import AudioUpdatable
from frontend.components.element.element import Element
from frontend.components.element.element_value import ElementValue
from frontend.components.textedit.textedit import TextEdit
from frontend.nodes.cnode import CNode
from frontend.nodes.stream.stream_player_node import StreamPlayerNode


class SCPlaylistPlayer(CNode, AudioUpdatable):
    nodeName = "SCPlaylistPlayer"

    def __init__(self, playlist_url="", browser="chrome", profile="Default", prefetch_seconds=10, render=True):
        super().__init__(self.nodeName, {"chunk": {"io": "out"}}, render=render)
        self.playlist_url = TextEdit(self, "playlist_url", ElementValue(playlist_url))
        self.browser = TextEdit(self, "browser", ElementValue(browser))
        self.profile = TextEdit(self, "profile", ElementValue(profile))
        self.prefetch_seconds = Element(self, "prefetch_seconds", ElementValue(float(prefetch_seconds)))
        self.chunk = Element(self, "chunk", ElementValue(np.zeros(1024, dtype=np.float32)))

        self.stream_player = StreamPlayerNode(render=False)
        self._thread = None
        self._stop_event = threading.Event()

        if playlist_url:
            self.start()

    def _ydl_opts(self):
        opts = {"quiet": True, "format": "bestaudio/best"}
        browser = str(self.browser.value).strip()
        profile = str(self.profile.value).strip()
        if browser:
            opts["cookiesfrombrowser"] = (browser, profile) if profile else (browser,)
        return opts

    @staticmethod
    def _extract_entries(url, opts):
        playlist_opts = dict(opts)
        playlist_opts["extract_flat"] = "in_playlist"
        playlist_opts["lazy_playlist"] = True
        with YoutubeDL(playlist_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return info.get("entries", [])

    @staticmethod
    def _download_track(entry, opts):
        track_url = entry.get("webpage_url") or entry.get("url")
        if not track_url:
            return None
        with tempfile.TemporaryDirectory() as tmp:
            dl_opts = dict(opts)
            dl_opts["outtmpl"] = os.path.join(tmp, "track.%(ext)s")
            dl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "0"}]
            YoutubeDL(dl_opts).download([track_url])
            wav_path = os.path.join(tmp, "track.wav")
            if not os.path.exists(wav_path):
                return None
            audio, sr = sf.read(wav_path)
            return audio, sr

    def _worker(self):
        url = str(self.playlist_url.value).strip()
        if not url:
            return
        opts = self._ydl_opts()
        entries = self._extract_entries(url, opts)
        if not entries:
            return

        idx = 0
        first = self._download_track(entries[idx], opts)
        while first is None and idx + 1 < len(entries):
            idx += 1
            first = self._download_track(entries[idx], opts)
        if first is None:
            return

        audio, sr = first
        self.stream_player.enqueue(audio, sr)
        self.stream_player.start()
        idx += 1

        while not self._stop_event.is_set() and idx < len(entries):
            remaining = self.stream_player.remaining_seconds_to_song_end()
            if remaining is not None and remaining <= float(self.prefetch_seconds.value):
                nxt = self._download_track(entries[idx], opts)
                if nxt is not None:
                    naudio, nsr = nxt
                    self.stream_player.enqueue(naudio, nsr)
                idx += 1
            else:
                time.sleep(0.1)

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self.stream_player.stop()

    def c_update(self):
        if self.chunk.value.shape[0] != self.stream_player.chunk.value.shape[0]:
            self.chunk.value = np.zeros_like(self.stream_player.chunk.value)
        self.chunk.value[:] = self.stream_player.chunk.value
        return self.chunk
