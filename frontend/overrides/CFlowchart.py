from PyQt5 import QtCore
from pyqtgraph.flowchart import Flowchart
from networkx.drawing.nx_pydot import graphviz_layout
import networkx as nx

class CFlowchart(Flowchart):
    def __init__(self, nodes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inputNode.graphicsItem().hide()
        self.outputNode.graphicsItem().hide()

        # self.viewBox.sigRangeChanged.connect(self.on_view_range_changed)
        self.add_nodes(nodes or [])
        self.visible_nodes = self.get_visible_nodes()
        ##!! change with visible nodes
        QtCore.QTimer.singleShot(0, lambda: self.place_nodes())

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

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)

    def add_node(self, node, name=None, pos=None):
        if name is None and hasattr(node, "name"):
            name = node.name()
        self.addNode(node, name, pos)
        return node

    def on_view_range_changed(self, *_):
        for node in self._nodes.values():
            refresh = getattr(node, "refresh_terminal_positions", None)
            if callable(refresh):
                refresh()

    def get_visible_nodes(self):
        return [
            node
            for node in self._nodes.values()
            if node.graphicsItem() is not None and node.graphicsItem().isVisible()
        ]

    def place_nodes(self):
        if not self.visible_nodes:
            return

        node_by_name = {node.name(): node for node in self.visible_nodes}
        graph = nx.DiGraph()
        graph.add_nodes_from(node_by_name.keys())

        for src_node in self.visible_nodes:
            src_name = src_node.name()
            for term in src_node.terminals.values():
                if not term.isOutput():
                    continue
                for connected_term in term.connections().keys():
                    dst_node = connected_term.node()
                    if dst_node in self.visible_nodes:
                        graph.add_edge(src_name, dst_node.name())

        positions = None
        if positions is None:
            if nx.is_directed_acyclic_graph(graph):
                for layer, nodes in enumerate(nx.topological_generations(graph)):
                    for node_name in nodes:
                        graph.nodes[node_name]["layer"] = layer
            else:
                condensed = nx.condensation(graph)
                comp_layer = {}
                for layer, components in enumerate(nx.topological_generations(condensed)):
                    for comp in components:
                        comp_layer[comp] = layer
                for node_name, comp in condensed.graph["mapping"].items():
                    graph.nodes[node_name]["layer"] = comp_layer[comp]

            positions = nx.multipartite_layout(graph, subset_key="layer", align="vertical")
            positions = {k: (float(v[0]) * 2000.0, float(v[1]) * 3000.0) for k, v in positions.items()}

        for node_name, (x, y) in positions.items():
            node_by_name[node_name].graphicsItem().setPos(float(x), float(-y))
