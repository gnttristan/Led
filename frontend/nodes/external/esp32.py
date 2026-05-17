import os
import signal
import subprocess
import sys
import threading
import time
from queue import Queue, Full

import numpy as np
import serial

from config import DELAY_UPDATE, FREQ_BINS
from backend.updatable.updatable import VisualUpdatable
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class ESP32Node(CNode, VisualUpdatable):
    nodeName = "ESP32"

    def __init__(
        self,
        rgb: np.ndarray = np.zeros((FREQ_BINS, 3), dtype=np.uint8),
        script_path: str = "esp32/main.py",
        port: str = "/dev/cu.usbserial-1410",
        led_count: int = FREQ_BINS,
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "rgb": {"io": "in"},
        }
        CNode.__init__(self, self.nodeName, terminals, render=render, alias=alias)
        VisualUpdatable.__init__(self)

        self.rgb = Element(self, "rgb", ElementValue(rgb))
        self.script_path = Element(self, "script_path", ElementValue(script_path))
        self.port = Element(self, "port", ElementValue(port))
        self.led_count = Element(self, "led_count", ElementValue(led_count))
        self.serial = serial.Serial(self.port.value, 115200, timeout=1, write_timeout=1)
        # self._reset_board()
        self.worker = threading.Thread(target=self._write_loop, daemon=True)
        self.worker.start()

    def c_update(self):
        pass

    def _write_loop(self):
        while True:
            self._write_frame(np.array(self.rgb.value, dtype=np.uint8).tobytes())
            time.sleep(DELAY_UPDATE / 1000.0)

    def _write_frame(self, frame):
        try:
            written = self.serial.write(frame)
            print("wrote", written, "of", len(frame))
            self.serial.flush()
        except serial.SerialTimeoutException:
            pass
        except serial.SerialException:
            self.serial = None

    def _reset_board(self):
        self._kill_port_users()
        subprocess.run(
            [
                sys.executable,
                "-m",
                "mpremote",
                "connect",
                self.port.value,
                "reset",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        time.sleep(2)

    def _kill_port_users(self):
        result = subprocess.run(
            ["lsof", "-t", self.port.value],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )

        current_pid = os.getpid()
        for line in result.stdout.splitlines():
            if not line.strip():
                continue

            pid = int(line)
            if pid == current_pid:
                continue
            if not self._is_mpremote_process(pid):
                continue

            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    def _is_mpremote_process(self, pid):
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        command = result.stdout.strip()
        return "mpremote" in command
