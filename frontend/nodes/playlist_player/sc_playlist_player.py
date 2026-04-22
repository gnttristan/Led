import os
import pickle
import tempfile
import threading
import hashlib
from urllib.parse import unquote, urlparse

import numpy as np
import soundfile as sf
from yt_dlp import YoutubeDL
from PyQt5 import QtCore

from backend.updatable.updatable import AudioUpdatable
from config import SAMPLE_RATE
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.components.elements.player.playlist_player import PlaylistPlayer
from frontend.components.elements.textedit.textedit import TextEdit
from frontend.nodes.cnode import CNode


class SCPlaylistPlayer(CNode, AudioUpdatable):
    nodeName = "SCPlaylistPlayer"
    entries_cache_path = os.path.expanduser("~/.cache/led/sc_playlist_entries.pkl")
    metadataReady = QtCore.pyqtSignal(object)
    trackLoaded = QtCore.pyqtSignal(int)

    def __init__(self,
             playlist_url: str = "https://soundcloud.com/trg-electro/sets/led",
             browser: str = "chrome",
             profile: str = "Default",
             prefetch_seconds: int | float = 10,
             render: bool = True
        ) -> None:
        super().__init__(
            self.nodeName,
            {"audio": {"io": "out"}, "sample_rate": {"io": "out"}, "enqueue_token": {"io": "out"}},
            render=render,
        )
        self.playlist_url = TextEdit(self, "playlist_url", ElementValue(playlist_url))
        self.browser = TextEdit(self, "browser", ElementValue(browser))
        self.profile = TextEdit(self, "profile", ElementValue(profile))
        self.prefetch_seconds = Element(self, "prefetch_seconds", ElementValue(float(prefetch_seconds)))
        self.audio = Element(self, "audio", ElementValue(np.zeros((0, 2), dtype=np.float32)))
        self.sample_rate = Element(self, "sample_rate", ElementValue(0))
        self.enqueue_token = Element(self, "enqueue_token", ElementValue(0))
        self.playlist_player = PlaylistPlayer([])
        self.elements.append(self.playlist_player)

        self.playlist_player.playRequested.connect(self.on_play_requested)
        self.playlist_player.pauseRequested.connect(self.on_pause_requested)
        self.playlist_player.seekRequested.connect(self.on_seek_requested)
        self.metadataReady.connect(self.on_metadata_ready)
        self.trackLoaded.connect(self.on_track_loaded)

        self._thread = None
        self._stop_event = threading.Event()
        self._data_lock = threading.Lock()
        self._tracks = []
        self._seek_ratios = []
        self._current_track_index = -1
        self._is_playing = False

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
        key_raw = f"{url}|{repr(sorted(opts.items()))}"
        cache_key = hashlib.sha256(key_raw.encode("utf-8")).hexdigest()
        cache = {}
        try:
            with open(SCPlaylistPlayer.entries_cache_path, "rb") as f:
                cache = pickle.load(f)
        except Exception:
            cache = {}
        if cache_key in cache:
            return cache[cache_key]

        playlist_opts = dict(opts)
        playlist_opts["extract_flat"] = "in_playlist"
        playlist_opts["lazy_playlist"] = True
        with YoutubeDL(playlist_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        entries = info.get("entries", [])

        cache[cache_key] = entries
        try:
            os.makedirs(os.path.dirname(SCPlaylistPlayer.entries_cache_path), exist_ok=True)
            with open(SCPlaylistPlayer.entries_cache_path, "wb") as f:
                pickle.dump(cache, f)
        except Exception:
            pass

        return entries

    @staticmethod
    def _download_track(entry, opts):
        track_url = entry.get("url")
        with tempfile.TemporaryDirectory() as tmp:
            dl_opts = dict(opts)
            dl_opts["outtmpl"] = os.path.join(tmp, "track.%(ext)s")
            dl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "0"}]
            dl_opts["postprocessor_args"] = ["-ar", str(SAMPLE_RATE), "-ac", "2"]
            YoutubeDL(dl_opts).download([track_url])
            wav_path = os.path.join(tmp, "track.wav")
            audio, sr = sf.read(wav_path)
            return audio, sr

    @staticmethod
    def _slug_to_text(value):
        return unquote((value or "").replace("-", " "))

    @classmethod
    def _entry_metadata(cls, entry):
        track_url = entry.get("url", "")
        parts = [p for p in urlparse(track_url).path.split("/") if p]
        artist_from_url = cls._slug_to_text(parts[0]) if len(parts) > 0 else ""
        title_from_url = cls._slug_to_text(parts[1]) if len(parts) > 1 else ""
        duration = entry.get("duration")
        return {
            "artist": artist_from_url,
            "title": title_from_url,
            "duration": float(duration) if duration else 0.0,
        }

    def _worker(self):
        url = str(self.playlist_url.value).strip()
        opts = self._ydl_opts()
        entries = self._extract_entries(url, opts)
        metadata = [self._entry_metadata(entry) for entry in entries]
        with self._data_lock:
            self._tracks = [None] * len(entries)
            self._seek_ratios = [0.0] * len(entries)
        self.metadataReady.emit(metadata)

        for idx, entry in enumerate(entries):
            if self._stop_event.is_set():
                break
            n_audio, n_sr = self._download_track(entry, opts)
            arr = np.asarray(n_audio, dtype=np.float32)
            arr = arr[:, None] if arr.ndim == 1 else arr
            with self._data_lock:
                self._tracks[idx] = (arr, int(n_sr))
            self.trackLoaded.emit(idx)

    def on_track_loaded(self, index):
        self.playlist_player.set_loaded(index, True)
        self._refresh_node_ui_geometry()

    def on_metadata_ready(self, metadata):
        self.playlist_player.set_playlist_metadata(metadata)
        self._refresh_node_ui_geometry()

    def _refresh_node_ui_geometry(self):
        self.playlist_player.adjustSize()
        self.refresh_terminal_positions()

    def on_play_requested(self, index):
        with self._data_lock:
            track = self._tracks[index]
            ratio = self._seek_ratios[index]
            self._current_track_index = index
        if track is None:
            return
        audio, sr = track
        start = int(ratio * audio.shape[0])
        self.audio.value = audio[start:]
        self.sample_rate.value = int(sr)
        self.enqueue_token.value = int(self.enqueue_token.value) + 1
        self._is_playing = True

    def on_pause_requested(self, index):
        if index != self._current_track_index:
            return
        self.audio.value = np.zeros((0, 2), dtype=np.float32)
        self.enqueue_token.value = int(self.enqueue_token.value) + 1
        self._is_playing = False

    def on_seek_requested(self, index, ratio):
        with self._data_lock:
            self._seek_ratios[index] = float(ratio)
            track = self._tracks[index]
        if index != self._current_track_index or not self._is_playing or track is None:
            return
        audio, sr = track
        start = int(float(ratio) * audio.shape[0])
        self.audio.value = audio[start:]
        self.sample_rate.value = int(sr)
        self.enqueue_token.value = int(self.enqueue_token.value) + 1

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self.audio.value = np.zeros((0, 2), dtype=np.float32)
        self.enqueue_token.value = int(self.enqueue_token.value) + 1
        self._is_playing = False

    def c_update(self):
        return self.audio
