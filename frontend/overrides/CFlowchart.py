import inspect

from PyQt5 import QtCore
from pyqtgraph.flowchart import Flowchart
import networkx as nx

from frontend.components.elements.element import Element
from frontend.components.ui.create_node_form import CreateNodeForm


class CFlowchart(Flowchart):
    UPDATE_PAUSE_MS = 150

    def __init__(self, nodes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pause_updates_until = 0
        self.widget().installEventFilter(self)
        self.inputNode.graphicsItem().hide()
        self.outputNode.graphicsItem().hide()

        # self.viewBox.sigRangeChanged.connect(self.on_view_range_changed)
        self.add_nodes(nodes or [])
        self.visible_nodes = self.get_visible_nodes()
        ##!! change with visible nodes
        QtCore.QTimer.singleShot(0, lambda: self.place_nodes())

    def eventFilter(self, obj, event):
        del obj
        if event.type() in (
            QtCore.QEvent.Type.MouseButtonPress,
            QtCore.QEvent.Type.MouseButtonRelease,
            QtCore.QEvent.Type.KeyPress,
            QtCore.QEvent.Type.Wheel,
        ):
            self.pause_updates()
        return False

    def pause_updates(self, duration_ms=None):
        if duration_ms is None:
            duration_ms = self.UPDATE_PAUSE_MS
        self._pause_updates_until = QtCore.QTime.currentTime().msecsSinceStartOfDay() + int(duration_ms)

    def should_pause_updates(self):
        return QtCore.QTime.currentTime().msecsSinceStartOfDay() < self._pause_updates_until

    def createNode(self, nodeType, name=None, pos=None):
        if name is None:
            n = 0
            while True:
                name = f"{nodeType}.{n}"
                if name not in self._nodes:
                    break
                n += 1
        node_cls = self.library.getNodeType(nodeType)
        node = node_cls(render=False)
        if not self.display_create_node_form(node):
            return None

        if hasattr(node, "rename") and node.name() != name:
            node.rename(name)
        self.addNode(node, name, pos)
        draw = getattr(node, "draw", None)
        if callable(draw):
            QtCore.QTimer.singleShot(0, draw)
        return node

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)

    def add_node(self, node, name=None, pos=None):
        if name is None and hasattr(node, "name"):
            name = node.name()
        self.addNode(node, name, pos)
        return node

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

    def display_create_node_form(self, node):
        node_name = node.name()
        node_args = list(dict(inspect.signature(node.__init__).parameters.items()).values())
        create_node_form = CreateNodeForm(self, node, node_name, node_args)
        return create_node_form.exec_() == CreateNodeForm.Accepted
