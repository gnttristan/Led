from backend.updatable.updatable import AudioUpdatable, VisualUpdatable


class AudioPipeline(AudioUpdatable):
    def __init__(self):
        super().__init__()

    def c_update(self):
        pass


class VisualPipeline(VisualUpdatable):
    def __init__(self):
        super().__init__()

    def c_update(self):
        pass