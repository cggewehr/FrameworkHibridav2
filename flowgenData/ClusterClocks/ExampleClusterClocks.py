import json
from decimal import Decimal

# ClusterClocks[BaseNoCPos] = Clock Period (in ns)
ClusterClocks = [None] * 9

ClusterClocks[0] = float(10)
ClusterClocks[1] = float(10)
ClusterClocks[2] = float(10)
ClusterClocks[3] = float(10)
ClusterClocks[4] = float(10)
ClusterClocks[5] = float(10)
ClusterClocks[6] = float(10)
ClusterClocks[7] = float(10)
ClusterClocks[8] = float(10)

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, complex):
            return [obj.real, obj.imag]
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

ClocksJSONString = json.dumps(ClusterClocks, sort_keys = False, indent = 4, cls=ComplexEncoder)

with open("ExampleClusterClocks.json", "w") as JSONFile:
    JSONFile.write(ClocksJSONString)
