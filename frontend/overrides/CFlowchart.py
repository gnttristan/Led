import inspect

import networkx as nx
from PyQt5 import QtCore
from pyqtgraph.debug import printExc
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.flowchart.Node import Node

from backend.updatable.updatable import pause_updates, audio_updatable_objects, visual_updatable_objects
from config import NODE_LAYOUT_X_GAP, NODE_LAYOUT_Y_GAP
from frontend.components.ui.create_node_form import CreateNodeForm
from frontend.overrides.CNode import CNode


class CFlowchart(Flowchart):
    def __init__(self, nodes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget().installEventFilter(self)
        self.inputNode.graphicsItem().hide()
        self.outputNode.graphicsItem().hide()

        # self.viewBox.sigRangeChanged.connect(self.on_view_range_changed)
        self.add_nodes(nodes or [])
        self.visible_nodes = self.get_visible_nodes()
        ##!! change with visible nodes
        QtCore.QTimer.singleShot(0, lambda: self.place_nodes())

    def eventFilter(self, obj, event):
        if event.type() in (
            QtCore.QEvent.Type.MouseButtonPress,
            QtCore.QEvent.Type.MouseButtonRelease,
            QtCore.QEvent.Type.KeyPress,
            QtCore.QEvent.Type.Wheel,
        ):
            pause_updates()
        return False

    def createNode(self, nodeType, name=None, pos=None, ctor_kwargs=None):
        needs_setup_form = name is None
        name = name or self._next_node_name(nodeType)

        node_cls = self.library.getNodeType(nodeType)
        node = node_cls(**self._node_init_kwargs(node_cls, name, ctor_kwargs))

        if needs_setup_form and not self.display_create_node_form(node):
            return None

        if hasattr(node, "rename") and node.name() != name:
            node.rename(name)
        if hasattr(node, "alias"):
            node.alias = name
        self.addNode(node, name, pos)
        if hasattr(node, "init_all"):
            node.init_all()
        draw = getattr(node, "draw", None)
        if callable(draw):
            QtCore.QTimer.singleShot(0, draw)
        return node

    def _next_node_name(self, node_type):
        index = 0
        while f"{node_type}.{index}" in self._nodes:
            index += 1
        return f"{node_type}.{index}"

    @staticmethod
    def _node_init_kwargs(node_cls, name, ctor_kwargs=None):
        init_kwargs = {"render": False, **(ctor_kwargs or {})}
        signature_parameters = inspect.signature(node_cls.__init__).parameters
        if "alias" in signature_parameters:
            init_kwargs.setdefault("alias", name)
        return {key: value for key, value in init_kwargs.items() if key in signature_parameters}

    def restoreState(self, state, clear=False):
        audio_updatable_objects.clear()
        visual_updatable_objects.clear()
        self.blockSignals(True)
        try:
            if clear:
                self.clear()
            Node.restoreState(self, state)
            nodes = state["nodes"]
            nodes.sort(key=lambda a: a["pos"][0])
            pending_nodes = list(nodes)
            while pending_nodes:
                progressed = False
                next_pending = []

                for node_state in pending_nodes:
                    name = node_state["name"]
                    if name in self._nodes:
                        self._nodes[name].restoreState(node_state["state"])
                        progressed = True
                        continue

                    try:
                        node = self._restore_node(node_state)
                        if node is None:
                            next_pending.append(node_state)
                            continue

                        progressed = True
                    except Exception:
                        printExc("Error creating node %s: (continuing anyway)" % name)
                        progressed = True

                if not progressed:
                    break
                pending_nodes = next_pending

            self.inputNode.restoreState(state.get("inputNode", {}))
            self.outputNode.restoreState(state.get("outputNode", {}))

            ##!! ToDo Look in depth and maybe change [#1] : preferable solution : keep Elements values Elements as
            ##!! ToDo Elements when load UI so no need to rebuild terminals here
            self._connect_saved_terminals(state["connects"])
        finally:
            self.blockSignals(False)

        self.outputChanged()
        self.sigChartLoaded.emit()
        self.sigStateChanged.emit()

    def _restore_node(self, node_state):
        ctor_kwargs = self._ctor_kwargs_from_state(node_state.get("state", {}))
        if ctor_kwargs is None:
            return None

        node = self.createNode(
            node_state["class"],
            name=node_state["name"],
            pos=node_state["pos"],
            ctor_kwargs=ctor_kwargs,
        )
        node.restoreState(node_state["state"])
        return node

    def _ctor_kwargs_from_state(self, state):
        ctor_kwargs = {
            key: CNode.deserialize_state_value(value)
            for key, value in state.get("ctor_kwargs", {}).items()
        }

        if not self._resolve_init_refs(ctor_kwargs, state.get("init_refs", {})):
            return None

        arguments = state.get("arguments")
        if arguments is not None:
            resolved_arguments = self._resolve_arguments(arguments)
            if resolved_arguments is None:
                return None
            ctor_kwargs["arguments"] = resolved_arguments

        return ctor_kwargs

    def _resolve_init_refs(self, ctor_kwargs, init_refs):
        for parameter_name, payload in init_refs.items():
            element = self._resolve_element_ref(payload.get("__element_ref__", {}))
            if element is None:
                return False
            ctor_kwargs[parameter_name] = element
        return True

    def _resolve_arguments(self, arguments):
        resolved = []
        for arg in arguments:
            if isinstance(arg, dict) and "__element_ref__" in arg:
                element = self._resolve_element_ref(arg["__element_ref__"])
                if element is None:
                    return None
                resolved.append(element)
            else:
                resolved.append(CNode.deserialize_state_value(arg))
        return resolved

    def _resolve_element_ref(self, ref):
        src_node = self._nodes.get(ref.get("node_name"))
        element_name = ref.get("element_name")
        if src_node is None or not hasattr(src_node, element_name):
            return None
        return getattr(src_node, element_name)

    def _connect_saved_terminals(self, connects):
        for n1, t1, n2, t2 in connects:
            try:
                node1 = self._nodes.get(n1)
                node2 = self._nodes.get(n2)
                if node1 is None or node2 is None:
                    continue
                if t1 not in node1.terminals or t2 not in node2.terminals:
                    continue
                self.connectTerminals(node1[t1], node2[t2])
            except Exception:
                printExc("Error connecting terminals %s.%s - %s.%s:" % (n1, t1, n2, t2))

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
        layers = self._layout_layers(node_by_name)
        positions = self._layout_positions(node_by_name, layers)
        for node_name, (x, y) in positions.items():
            node_by_name[node_name].graphicsItem().setPos(float(x), float(y))

    def _layout_layers(self, node_by_name):
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

        if nx.is_directed_acyclic_graph(graph):
            return [list(nodes) for nodes in nx.topological_generations(graph)]

        condensed = nx.condensation(graph)
        mapping = condensed.graph["mapping"]
        return [
            [
                node_name
                for node_name, component in mapping.items()
                if component in components
            ]
            for components in nx.topological_generations(condensed)
        ]

    def _layout_positions(self, node_by_name, layers):
        x_gap = float(NODE_LAYOUT_X_GAP)
        y_gap = float(NODE_LAYOUT_Y_GAP)
        positions = {}
        x = 0.0
        for layer_nodes in layers:
            layer_width = max(self._layout_node_size(node_by_name[name])[0] for name in layer_nodes)
            layer_height = sum(self._layout_node_size(node_by_name[name])[1] for name in layer_nodes)
            layer_height += y_gap * max(0, len(layer_nodes) - 1)
            y = -layer_height / 2.0
            for node_name in sorted(layer_nodes):
                _, node_height = self._layout_node_size(node_by_name[node_name])
                positions[node_name] = (x, y + node_height / 2.0)
                y += node_height + y_gap
            x += layer_width + x_gap

        return positions

    def _layout_node_size(self, node):
        item = node.graphicsItem()
        rect = item.boundingRect()
        width = max(float(rect.width()), 180.0)
        height = max(float(rect.height()), 100.0)

        group_nodes = getattr(node, "nodes", None)
        if group_nodes:
            visible_children = [child for child in group_nodes if getattr(child, "render", False)]
            if visible_children:
                child_sizes = [self._layout_node_size(child) for child in visible_children]
                child_widths = [child_width for child_width, _ in child_sizes]
                child_heights = [child_height for _, child_height in child_sizes]
                width = max(width, sum(child_widths) + 360.0 * max(0, len(child_widths) - 1))
                height = max(height, max(child_heights))

        return width, height

    def display_create_node_form(self, node):
        node_name = node.name()
        node_args = list(dict(inspect.signature(node.__init__).parameters.items()).values())
        create_node_form = CreateNodeForm(self, node, node_name, node_args)
        return create_node_form.exec_() == CreateNodeForm.Accepted
