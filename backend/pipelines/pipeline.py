from backend.updatable.updatable import AudioUpdatable, VisualUpdatable


class AudioPipeline(AudioUpdatable):
    def __init__(self):
        super().__init__()

    def update(self):
        pass


class VisualPipeline(VisualUpdatable):
    def __init__(self):
        super().__init__()

    def update(self):
        pass