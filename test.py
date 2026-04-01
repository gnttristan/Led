from yt_dlp import YoutubeDL
import numpy as np
import sounddevice as sd
import soundfile as sf
import tempfile, os
import threading
import time
from collections import deque


def sc_playlist_arrays(url, ydl_opts):
    playlist_opts = dict(ydl_opts)
    playlist_opts["extract_flat"] = "in_playlist"  # key fix
    playlist_opts["lazy_playlist"] = True  # optional, lower burst calls
    with YoutubeDL(playlist_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info.get("entries", [])

def sc_song_array(_ydl, ydl_opts, entry):
    track_url = entry.get("webpage_url") or entry.get("url")
    if not track_url:
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        download_opts = dict(ydl_opts)
        download_opts["outtmpl"] = os.path.join(tmpdir, "track.%(ext)s")
        download_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "0",
        }]
        YoutubeDL(download_opts).download([track_url])

        wav_path = os.path.join(tmpdir, "track.wav")
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"WAV not generated for {track_url}")

        audio, sr = sf.read(wav_path)
        return audio, sr


class PlaybackState:
    def __init__(self, initial_audio, sr, entries, ydl, ydl_opts, start_next_index):
        self.lock = threading.Lock()
        self.buffer_updated = threading.Condition(self.lock)
        self.blocks_updated = threading.Condition(self.lock)
        self.samples_written = 0
        self.finished = False
        self.stop_event = threading.Event()
        self.last_50_amplitudes = np.zeros(50, dtype=np.float32)
        self.audio_buffer = initial_audio.astype(np.float32, copy=False)
        self.song_end_samples = [self.audio_buffer.shape[0]]
        self.sr = sr
        self.entries = entries
        self.next_entry_index = start_next_index
        self.ydl = ydl
        self.ydl_opts = ydl_opts
        self.loading_next = False
        self.block_queue = deque()


def to_2d_float32(audio):
    audio_2d = audio[:, None] if audio.ndim == 1 else audio
    return audio_2d.astype(np.float32, copy=False)


def play_audio_thread(state, block_size=1024):
    channels = state.audio_buffer.shape[1]

    with sd.Output????(samplerate=state.sr, channels=channels, dtype="float32", blocksize=block_size) as ????:
        index = 0
        while not state.stop_event.is_set():
            with state.lock:
                total = state.audio_buffer.shape[0]
                if index >= total:
                    if state.next_entry_index >= len(state.entries) and not state.loading_next:
                        break
                    state.buffer_updated.wait(timeout=0.05)
                    continue

            end = min(index + block_size, total)
            block = state.audio_buffer[index:end]
            ????.write(block)

            mono_block = block[:, 0] if block.shape[1] == 1 else np.mean(block, axis=1)
            with state.lock:
                state.samples_written = end
                state.block_queue.append(mono_block.copy())
                state.blocks_updated.notify()
            index = end

    with state.lock:
        state.finished = True
        state.blocks_updated.notify_all()


def amplitude_roll_thread(state):
    local_buffer = np.zeros(50, dtype=np.float32)

    while True:
        with state.lock:
            while not state.block_queue and not state.finished:
                state.blocks_updated.wait(timeout=0.05)
            if not state.block_queue and state.finished:
                break
            chunk = state.block_queue.popleft()

        amplitude = float(np.sqrt(np.mean(np.square(chunk)))) if chunk.size else 0.0
        local_buffer = np.roll(local_buffer, -1)
        local_buffer[-1] = amplitude
        with state.lock:
            state.last_50_amplitudes[:] = local_buffer


def prefetch_next_song_thread(state, trigger_seconds=10.0):
    while not state.stop_event.is_set():
        with state.lock:
            if state.finished:
                break
            if state.next_entry_index >= len(state.entries):
                pass
            else:
                song_start = 0
                current_song_end = None
                for end_sample in state.song_end_samples:
                    if state.samples_written < end_sample:
                        current_song_end = end_sample
                        break
                    song_start = end_sample

                if current_song_end is not None:
                    remaining_samples = current_song_end - state.samples_written
                    remaining_seconds = remaining_samples / float(state.sr)
                    should_load = remaining_seconds <= trigger_seconds and not state.loading_next
                    if should_load:
                        entry_index = state.next_entry_index
                        state.loading_next = True
                    else:
                        entry_index = None
                else:
                    entry_index = None

        if entry_index is None:
            time.sleep(0.05)
            continue

        result = sc_song_array(state.ydl, state.ydl_opts, state.entries[entry_index])
        with state.lock:
            if result is not None:
                next_audio, next_sr = result
                if next_sr == state.sr:
                    next_audio_2d = to_2d_float32(next_audio)
                    state.audio_buffer = np.vstack((state.audio_buffer, next_audio_2d))
                    state.song_end_samples.append(state.audio_buffer.shape[0])
                    state.next_entry_index += 1
                    state.buffer_updated.notify_all()
                else:
                    print(f"Skipping track at index {entry_index}: sample rate {next_sr} != {state.sr}")
                    state.next_entry_index += 1
            else:
                state.next_entry_index += 1
            state.loading_next = False

        time.sleep(0.01)

    with state.lock:
        state.buffer_updated.notify_all()

browser = "chrome"
profile = "Default"

ydl_opts = {"quiet": True, "format": "bestaudio/best"}
if browser:
    ydl_opts["cookiesfrombrowser"] = (browser, profile) if profile else (browser,)

with YoutubeDL(ydl_opts) as ydl:
    URL = "https://soundcloud.com/user-519603245/sets/do-not-listen-to-this-playlist"
    entries = sc_playlist_arrays(URL, ydl_opts)
    first = None
    first_index = None
    for i, entry in enumerate(entries):
        first = sc_song_array(ydl, ydl_opts, entry)
        if first is not None:
            first_index = i
            break
    if first is None:
        raise RuntimeError("No playable song found in playlist")

    first_audio, sr = first
    state = PlaybackState(
        initial_audio=to_2d_float32(first_audio),
        sr=sr,
        entries=entries,
        ydl=ydl,
        ydl_opts=ydl_opts,
        start_next_index=first_index + 1,
    )

    player = threading.Thread(target=play_audio_thread, args=(state,), daemon=True)
    roller = threading.Thread(target=amplitude_roll_thread, args=(state,), daemon=True)
    prefetcher = threading.Thread(target=prefetch_next_song_thread, args=(state, 10.0), daemon=True)

    player.start()
    roller.start()
    prefetcher.start()

    player.join()
    state.stop_event.set()
    roller.join()
    prefetcher.join()

    print(state.last_50_amplitudes)
