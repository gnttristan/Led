import hashlib
import os
import pickle
import tempfile
import threading
import time
from urllib.parse import unquote, urlparse

import numpy as np
import soundfile as sf
from PyQt5 import QtCore
from yt_dlp import YoutubeDL

from backend.updatable.updatable import AudioUpdatable
from config import SAMPLE_RATE
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.components.elements.player.playlist_player import PlaylistPlayer
from frontend.components.elements.textedit.textedit import TextEdit
from frontend.nodes.playlist_player.soundcloud.api import search_tracks
from frontend.overrides.CNode import CNode


class SCPlaylistPlayer(CNode, AudioUpdatable):
    nodeName = "SCPlaylistPlayer"
    entries_cache_path = os.path.expanduser("~/.cache/led/sc_playlist_entries.pkl")
    tracks_cache_path = os.path.expanduser("~/.cache/led/sc_playlist_tracks.pkl")
    metadataReady = QtCore.pyqtSignal(object)
    trackLoaded = QtCore.pyqtSignal(int)

    def __init__(self, playlist_url="https://soundcloud.com/trg-electro/sets/led", browser="chrome", profile="Default", prefetch_seconds=10, cache=True, render=True, alias=None):
        super().__init__(self.nodeName, {"audio": {"io": "out"}, "sample_rate": {"io": "out"}, "enqueue_token": {"io": "out"}}, render=render, alias=alias)
        AudioUpdatable.__init__(self)
        self.playlist_url = TextEdit(self, "playlist_url", ElementValue(playlist_url))
        self.browser = TextEdit(self, "browser", ElementValue(browser))
        self.profile = TextEdit(self, "profile", ElementValue(profile))
        self.prefetch_seconds = Element(self, "prefetch_seconds", ElementValue(float(prefetch_seconds)))
        self.cache = Element(self, "cache", ElementValue(bool(cache)))
        self.audio = Element(self, "audio", ElementValue(np.zeros((0, 2), dtype=np.float32)))
        self.sample_rate = Element(self, "sample_rate", ElementValue(0))
        self.enqueue_token = Element(self, "enqueue_token", ElementValue(0))
        self.playlist_player = PlaylistPlayer([])
        self.elements.append(self.playlist_player)
        self.playlist_player.playRequested.connect(self.on_play_requested)
        self.playlist_player.pauseRequested.connect(self.on_pause_requested)
        self.playlist_player.seekRequested.connect(self.on_seek_requested)
        self.playlist_player.searchRequested.connect(self.search_music)
        self.playlist_player.searchResults.connect(self.playlist_player.set_search_results)
        self.playlist_player.addRequested.connect(self.add_music)
        self.playlist_player.removeRequested.connect(self.remove_music)
        self.metadataReady.connect(self.on_metadata_ready)
        self.trackLoaded.connect(self.on_track_loaded)
        self._thread = None
        self._stop_event = threading.Event()
        self._data_lock = threading.Lock()
        self._tracks = []
        self._entries = []
        self._seek_ratios = []
        self._current_track_index = -1
        self._is_playing = False
        self._track_started_at = 0.0
        self._track_start_position = 0.0
        if playlist_url:
            self.playlist_player.set_loading(True)
            self.start()

    def _ydl_opts(self):
        opts = {"quiet": True, "format": "bestaudio/best"}
        browser = str(self.browser.value).strip()
        profile = str(self.profile.value).strip()
        if browser:
            opts["cookiesfrombrowser"] = (browser, profile) if profile else (browser,)
        return opts

    @staticmethod
    def _load_cache(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception:
            return {}

    @staticmethod
    def _save_cache(path, cache):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(cache, f)

    @classmethod
    def _track_cache_key(cls, track_url, opts):
        return hashlib.sha256(f"{track_url}|{repr(sorted(opts.items()))}".encode()).hexdigest()

    @classmethod
    def _download_track(cls, entry, opts, use_cache=True):
        track_url = entry.get("url")
        if not track_url:
            return np.zeros((0, 2), dtype=np.float32), SAMPLE_RATE
        key = cls._track_cache_key(track_url, opts)
        cache = cls._load_cache(cls.tracks_cache_path) if use_cache else {}
        if key in cache:
            return cache[key]
        with tempfile.TemporaryDirectory() as tmp:
            download_opts = dict(opts)
            download_opts["outtmpl"] = os.path.join(tmp, "track.%(ext)s")
            download_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "0"}]
            download_opts["postprocessor_args"] = ["-ar", str(SAMPLE_RATE), "-ac", "2"]
            YoutubeDL(download_opts).download([track_url])
            audio, sample_rate = sf.read(os.path.join(tmp, "track.wav"))
            audio = np.asarray(audio, dtype=np.float32)
            audio = audio[:, None] if audio.ndim == 1 else audio
            result = audio, int(sample_rate)
        cache[key] = result
        try:
            cls._save_cache(cls.tracks_cache_path, cache)
        except Exception:
            pass
        return result

    @staticmethod
    def _entry_metadata(entry):
        url = entry.get("url", "")
        parts = [part for part in urlparse(url).path.split("/") if part]
        return {
            "artist": unquote(parts[0].replace("-", " ")) if parts else entry.get("uploader", ""),
            "title": unquote(parts[1].replace("-", " ")) if len(parts) > 1 else entry.get("title", ""),
            "duration": float(entry.get("duration") or 0),
        }

    @staticmethod
    def _extract_entries(url, opts):
        playlist_opts = dict(opts)
        playlist_opts.update(extract_flat="in_playlist", lazy_playlist=True)
        with YoutubeDL(playlist_opts) as ydl:
            return ydl.extract_info(url, download=False).get("entries", [])

    def _worker(self):
        try:
            opts = self._ydl_opts()
            entries = self._extract_entries(str(self.playlist_url.value).strip(), opts)
        except Exception:
            self.playlist_player.loadingChanged.emit(False)
            return
        with self._data_lock:
            self._entries = list(entries)
            self._tracks = [None] * len(entries)
            self._seek_ratios = [0.0] * len(entries)
        self.metadataReady.emit([self._entry_metadata(entry) for entry in entries])
        for index, entry in enumerate(entries):
            if self._stop_event.is_set():
                break
            with self._data_lock:
                self._tracks[index] = self._download_track(entry, opts, bool(self.cache.value))
            self.trackLoaded.emit(index)

    def search_music(self, query):
        self.playlist_player.set_loading(True)
        threading.Thread(target=self._search_worker, args=(query,), daemon=True).start()

    def _search_worker(self, query):
        try:
            results = search_tracks(query, self._ydl_opts(), limit=10)
        except Exception:
            results = []
        self.playlist_player.searchResults.emit(results)

    def add_music(self, entry):
        threading.Thread(target=self._add_worker, args=(entry,), daemon=True).start()

    def _add_worker(self, entry):
        try:
            opts = self._ydl_opts()
            track = self._download_track(entry, opts, bool(self.cache.value))
        except Exception:
            self.playlist_player.loadingChanged.emit(False)
            return
        with self._data_lock:
            self._entries.append(entry)
            self._tracks.append(track)
            self._seek_ratios.append(0.0)
            index = len(self._entries) - 1
            metadata = [self._entry_metadata(item) for item in self._entries]
        self.metadataReady.emit(metadata)
        self.trackLoaded.emit(index)

    def remove_music(self, index):
        with self._data_lock:
            if not 0 <= index < len(self._entries):
                return
            self._entries.pop(index)
            self._tracks.pop(index)
            self._seek_ratios.pop(index)
            metadata = [self._entry_metadata(item) for item in self._entries]
        self.metadataReady.emit(metadata)

    def on_metadata_ready(self, metadata):
        self.playlist_player.set_playlist_metadata(metadata)
        if not metadata:
            self.playlist_player.set_loading(False)
        self._refresh_node_ui_geometry()

    def on_track_loaded(self, index):
        with self._data_lock:
            track = self._tracks[index]
        if track is not None and index < len(self.playlist_player.music_players):
            audio, sample_rate = track
            player = self.playlist_player.music_players[index]
            player.music_length = audio.shape[0] / float(sample_rate or SAMPLE_RATE)
            player.music_length_label.setText(player.format_time(player.music_length))
        self.playlist_player.set_loaded(index, True)
        with self._data_lock:
            finished = index == len(self._tracks) - 1
        if finished:
            self.playlist_player.set_loading(False)
        self._refresh_node_ui_geometry()

    def _refresh_node_ui_geometry(self):
        self.playlist_player.adjustSize()
        if self._elements_proxy is not None and "audio" in self.terminals:
            self.refresh_terminal_positions()

    def on_play_requested(self, index):
        with self._data_lock:
            track = self._tracks[index]
            ratio = self._seek_ratios[index]
            self._current_track_index = index
        if track is None:
            return
        audio, sample_rate = track
        start = int(ratio * audio.shape[0])
        self._track_start_position = start / float(sample_rate or SAMPLE_RATE)
        self._track_started_at = time.monotonic()
        self.playlist_player.set_position(index, self._track_start_position)
        self.audio.value = audio[start:]
        self.sample_rate.value = int(sample_rate)
        self.enqueue_token.value = int(self.enqueue_token.value) + 1
        self._is_playing = True

    def on_pause_requested(self, index):
        if index != self._current_track_index:
            return
        self.audio.value = np.zeros((0, 2), dtype=np.float32)
        self.enqueue_token.value = int(self.enqueue_token.value) + 1
        self._seek_ratios[index] = self._current_position_ratio()
        self._is_playing = False

    def on_seek_requested(self, index, ratio):
        with self._data_lock:
            self._seek_ratios[index] = float(ratio)
            track = self._tracks[index]
        if index != self._current_track_index or not self._is_playing or track is None:
            return
        audio, sample_rate = track
        start = int(float(ratio) * audio.shape[0])
        self._track_start_position = start / float(sample_rate or SAMPLE_RATE)
        self._track_started_at = time.monotonic()
        self.playlist_player.set_position(index, self._track_start_position)
        self.audio.value = audio[start:]
        self.sample_rate.value = int(sample_rate)
        self.enqueue_token.value = int(self.enqueue_token.value) + 1

    def _current_position_ratio(self):
        if self._current_track_index < 0:
            return 0.0
        with self._data_lock:
            track = self._tracks[self._current_track_index]
        if track is None:
            return 0.0
        audio, sample_rate = track
        duration = audio.shape[0] / float(sample_rate or SAMPLE_RATE)
        return min(1.0, self._current_position() / duration) if duration else 0.0

    def _current_position(self):
        return self._track_start_position if not self._is_playing else self._track_start_position + time.monotonic() - self._track_started_at

    def _update_playback_position(self):
        if self._current_track_index < 0 or not self._is_playing:
            return
        position = self._current_position()
        self.playlist_player.set_position(self._current_track_index, position)
        ratio = self._current_position_ratio()
        with self._data_lock:
            self._seek_ratios[self._current_track_index] = ratio

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
        self._update_playback_position()
        return self.audio
