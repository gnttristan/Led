from pyqtgraph.flowchart import Node

from backend.attributes.attribute import AttributeType


class CNode(Node):
    def __init__(self, obj):
        self.obj = obj()

        obj_attributes = self.obj.__dict__.items()
        input_params = {
            name: {"io": "in"} for name, attr in obj_attributes
            if getattr(attr, "attr_type", None) == AttributeType.IN
        }
        output_params = {
            name: {"io": "out"} for name, attr in self.obj.__dict__.items()
            if getattr(attr, "attr_type", None) == AttributeType.OUT
        }

        self.input_params = tuple(input_params.keys())
        self.output_params = tuple(output_params.keys())
        terminals = input_params | output_params
        super().__init__(obj.__name__, terminals=terminals)

    def process(self, display=True, **kwargs):
        for name in self.input_params:
            value = kwargs.get(name)
            if value is not None:
                getattr(self.obj, name).value = value

        self.obj.update()

        return {
            name: getattr(self.obj, name).value
            for name in self.output_params
        }
