from pyqtgraph.flowchart import Flowchart


class CFlowchart(Flowchart):
    def createNode(self, nodeType, name=None, pos=None):
        if name is None:
            n = 0
            while True:
                name = f"{nodeType}.{n}"
                if name not in self._nodes:
                    break
                n += 1
        node_cls = self.library.getNodeType(nodeType)
        try:
            node = node_cls()
        except TypeError:
            node = node_cls(name)
        if hasattr(node, "rename") and node.name() != name:
            node.rename(name)
        self.addNode(node, name, pos)
        return node