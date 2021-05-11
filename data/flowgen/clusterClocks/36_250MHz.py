import json
from decimal import Decimal

# ClusterClocks[BaseNoCPos] = Clock Period (in ns)
ClusterClocks = [float(4)] * 36

ClocksJSONString = json.dumps(ClusterClocks, sort_keys = False, indent = 4)

with open("36_250MHz.json", "w") as JSONFile:
    JSONFile.write(ClocksJSONString)
