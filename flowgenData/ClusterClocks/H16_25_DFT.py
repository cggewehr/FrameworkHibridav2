
import json

ClusterClocks = [None] * 9

ClusterClocks[0] = 10
ClusterClocks[1] = 10
ClusterClocks[2] = 10
ClusterClocks[3] = 10
ClusterClocks[4] = 10
ClusterClocks[5] = 10
ClusterClocks[6] = 10
ClusterClocks[7] = 10
ClusterClocks[8] = 10

ClocksJSONString = json.dumps(ClusterClocks, sort_keys = False, indent = 4)

with open("H16_25_DFT.json", "w") as JSONFile:
    JSONFile.write(ClocksJSONString)
