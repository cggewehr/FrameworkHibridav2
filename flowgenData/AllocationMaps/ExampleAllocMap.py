import json

# AllocMap[PEPos] = App.Thread
AllocArray = [None] * 25

AllocArray[0] = None
AllocArray[1] = "PIP_B.OpDisp"
AllocArray[2] = "PIP_B.InpMemA"
AllocArray[3] = "PIP.JUG1"
AllocArray[4] = "PIP_B.MEM"
AllocArray[5] = "PIP_A.InpMemA"
AllocArray[6] = "PIP_A.HS"
AllocArray[7] = "PIP_A.InpMemB"
AllocArray[8] = "PIP.VS"
AllocArray[9] = "PIP_B.VS"
AllocArray[10] = "PIP.InpMemA"
AllocArray[11] = "PIP.HS"
AllocArray[12] = "PIP.InpMemB"
AllocArray[13] = "PIP_A.OpDisp"
AllocArray[14] = "PIP_B.HS"
AllocArray[15] = "PIP_A.InpMemB"
AllocArray[16] = "PIP_A.JUG1"
AllocArray[17] = "PIP_A.JUG2"
AllocArray[18] = "PIP_A.MEM"
AllocArray[19] = "PIP_B.JUG2"
AllocArray[20] = "PIP.JUG2"
AllocArray[21] = "PIP.MEM"
AllocArray[22] = "PIP.OpDisp"
AllocArray[23] = "PIP_B.InpMemB"
AllocArray[24] = "PIP_B.JUG1"

AllocJSONString = json.dumps(AllocArray, sort_keys = False, indent = 4)

with open("ExampleAllocMap.json", "w") as JSONFile:
    JSONFile.write(AllocJSONString)
