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

ClocksJSONString = json.dumps(ClusterClocks, sort_keys = False, indent = 4)

with open("ExampleClusterClocks.json", "w") as JSONFile:
    JSONFile.write(ClocksJSONString)
