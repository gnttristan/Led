from PyQt5 import QtCore

from frontend.nodes.cnode import CNode

audio_updatable_objects = []
visual_updatable_objects = []


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
