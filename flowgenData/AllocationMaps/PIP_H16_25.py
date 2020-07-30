
AllocArray = [None] * 25

AllocArray[0] = "PIP.HS"
AllocArray[1] = "PIP.VS"
AllocArray[2] = "PIP.JUG1"
AllocArray[3] = "PIP.JUG2"
AllocArray[4] = "PIP.InpMemA"
AllocArray[5] = "PIP.InpMemB"
AllocArray[6] = "PIP.MEM"
AllocArray[7] = "PIP.OpDisp"

import json

AllocJSONString = json.dumps(AllocArray, sort_keys = False, indent = 4)

with open("PIP_H16_25.json", "w") as JSONFile:
    JSONFile.write(AllocJSONString)

