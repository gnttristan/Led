import numpy as np

from config import FFT_SIZE, FREQ_BINS
from backend.updatable.updatable import AudioUpdatable
from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.enums.cut_side.cut_side_mode import CutSideMode
from frontend.overrides.CNode import CNode


class OutboundsFctNode(CNode, AudioUpdatable):
    nodeName = "OutboundsFct"

    def __init__(
        self,
        y_outbound: float = 1,
        y_center: float = -2,
        y_offset: float = 0,
        cute_side_mode: CutSideMode = CutSideMode.NONE,
        length: int = FREQ_BINS,
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "y_outbound": {"io": "in"},
            "y_center": {"io": "in"},
            "y_offset": {"io": "in"},
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render, alias=alias)

        self.y_outbound = Element(self, "y", ElementValue(y_outbound))
        self.y_center = Element(self, "y_center", ElementValue(y_center))
        self.y_offset = Element(self, "y_offset", ElementValue(y_offset))
        self.cute_side_mode = Element(self, "cute_side_mode", ElementValue(cute_side_mode))
        self.length = Element(self, "length", ElementValue(length))
        self.data = Element(self, "data", ElementValue(np.zeros(self.length.value)))

    def c_update(self):
        half_part = np.linspace(self.y_outbound.value, self.y_center.value, self.length.value // 2).flatten()
        mirrored = np.maximum(
            np.concatenate(((h:=half_part), h[::-1])),
            0
        )
        offsetted = np.roll(mirrored, self.y_offset.value * self.length.value)

        if self.cute_side_mode != CutSideMode.NONE:
            tray_edge_index = np.argsort(offsetted)[0 if self.cute_side_mode == CutSideMode.LEFT else 1]
            tray_edge_value = offsetted[tray_edge_index]
            fixed_array = np.hstack((
                np.repeat(tray_edge_value, tray_edge_index + 1 if self.cute_side_mode == CutSideMode.LEFT else 0),
                offsetted[tray_edge_index + 1:],
                np.repeat(tray_edge_value, 0 if self.cute_side_mode == CutSideMode.LEFT else tray_edge_index + 1)
            ))
            self.data.value[:] = fixed_array
            return

        self.data.value[:] = offsetted






