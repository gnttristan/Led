from frontend.components.elements.element import Element
from frontend.components.elements.element_value import ElementValue
from frontend.overrides.CNode import CNode


class RoutingNode(CNode):
    nodeName = "Routing"

    def __init__(
        self,
        operator_nodes: list[CNode] | None = None,
        render: bool = True,
        alias: str | None = None,
    ) -> None:
        terminals = {
            "data": {"io": "out"},
        }
        super().__init__(self.nodeName, terminals, render=render, alias=alias)

        self.operator_nodes = Element(self, "operator_nodes", ElementValue(operator_nodes or []))

    def c_update(self):
        pass
