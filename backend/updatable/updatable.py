from PyQt5 import QtCore

from frontend.overrides.CNode import CNode

audio_updatable_objects = []
visual_updatable_objects = []
_pause_updates_until = 0


def pause_updates(duration_ms=150):
    global _pause_updates_until
    _pause_updates_until = QtCore.QTime.currentTime().msecsSinceStartOfDay() + int(duration_ms)


class Updatable:
    def __init__(self):
        pass

    def c_update(self):
        pass


class AudioUpdatable(Updatable):
    def __init__(self):
        super().__init__()
        if isinstance(self, CNode):
            QtCore.QTimer.singleShot(0, lambda: audio_updatable_objects.append(self))
            return

        audio_updatable_objects.append(self)

    def c_update(self):
        super().c_update()


class VisualUpdatable(Updatable):
    def __init__(self):
        super().__init__()
        visual_updatable_objects.append(self)

    def c_update(self):
        super().c_update()
