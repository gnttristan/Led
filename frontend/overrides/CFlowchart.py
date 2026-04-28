import inspect

from PyQt5 import QtCore
from pyqtgraph.debug import printExc
from pyqtgraph.flowchart.Node import Node
from pyqtgraph.flowchart import Flowchart
import networkx as nx

from backend.updatable.updatable import pause_updates, audio_updatable_objects, visual_updatable_objects
from frontend.components.elements.element import Element
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
        if name is None:
            n = 0
            while True:
                name = f"{nodeType}.{n}"
                if name not in self._nodes:
                    break
                n += 1
        node_cls = self.library.getNodeType(nodeType)
        init_kwargs = {"render": False}
        init_kwargs.update(ctor_kwargs or {})
        signature_parameters = inspect.signature(node_cls.__init__).parameters
        if "alias" in signature_parameters and "alias" not in init_kwargs:
            init_kwargs["alias"] = name
        init_kwargs = {k: v for k, v in init_kwargs.items() if k in signature_parameters}
        node = node_cls(**init_kwargs)
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

                for n in pending_nodes:
                    if n["name"] in self._nodes:
                        self._nodes[n["name"]].restoreState(n["state"])
                        progressed = True
                        continue

                    try:
                        ctor_kwargs = {
                            key: CNode.deserialize_state_value(value)
                            for key, value in n.get("state", {}).get("ctor_kwargs", {}).items()
                        }
                        init_refs = n.get("state", {}).get("init_refs", {})
                        unresolved = False
                        for parameter_name, payload in init_refs.items():
                            ref = payload.get("__element_ref__", {})
                            src_node = self._nodes.get(ref.get("node_name"))
                            element_name = ref.get("element_name")
                            if src_node is None or not hasattr(src_node, element_name):
                                unresolved = True
                                break
                            ctor_kwargs[parameter_name] = getattr(src_node, element_name)

                        if unresolved:
                            next_pending.append(n)
                            continue

                        arguments = n.get("state", {}).get("arguments")
                        if arguments is not None:
                            resolved_arguments = []
                            unresolved = False
                            for arg in arguments:
                                if isinstance(arg, dict) and "__element_ref__" in arg:
                                    ref = arg["__element_ref__"]
                                    src_node = self._nodes.get(ref.get("node_name"))
                                    element_name = ref.get("element_name")
                                    if src_node is None or not hasattr(src_node, element_name):
                                        unresolved = True
                                        break
                                    resolved_arguments.append(getattr(src_node, element_name))
                                else:
                                    resolved_arguments.append(CNode.deserialize_state_value(arg))
                            if unresolved:
                                next_pending.append(n)
                                continue
                            ctor_kwargs["arguments"] = resolved_arguments

                        node = self.createNode(n["class"], name=n["name"], pos=n["pos"], ctor_kwargs=ctor_kwargs)
                        node.restoreState(n["state"])
                        progressed = True
                    except Exception:
                        printExc("Error creating node %s: (continuing anyway)" % n["name"])
                        progressed = True

                if not progressed:
                    break
                pending_nodes = next_pending

            self.inputNode.restoreState(state.get("inputNode", {}))
            self.outputNode.restoreState(state.get("outputNode", {}))

            ##!! ToDo Look in depth and maybe change [#1] : preferable solution : keep Elements values Elements as
            ##!! ToDo Elements when load UI so no need to rebuild terminals here
            for n1, t1, n2, t2 in state["connects"]:
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
        finally:
            self.blockSignals(False)

        self.outputChanged()
        self.sigChartLoaded.emit()
        self.sigStateChanged.emit()

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
