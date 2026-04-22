import numpy as np
from typing import Callable

from frontend.nodes.window.window import WindowNode

class WindowFct:
    def __init__(
        self,
        window: WindowNode,
        aggregation: Callable[[np.ndarray], None] | None = None
    ) -> None:
        self.data = np.zeros(window.data.value.shape[-1])
        self.aggregation = aggregation or self.aggregate
        window.window_fcts.value.append(self)

    def aggregate(self, window_data):
        return
