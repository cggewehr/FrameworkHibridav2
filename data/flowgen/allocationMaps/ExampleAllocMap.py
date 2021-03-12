import json

# AllocMap[PEPos] = $App.$Thread
AllocArray = [None] * 25

AllocArray[0] = None
AllocArray[1] = "PIP_3.OpDisp"
AllocArray[2] = "PIP_3.InpMemA"
AllocArray[3] = "PIP_1.JUG1"
AllocArray[4] = "PIP_3.MEM"
AllocArray[5] = "PIP_2.InpMemA"
AllocArray[6] = "PIP_2.HS"
AllocArray[7] = "PIP_2.InpMemB"
AllocArray[8] = "PIP_1.VS"
AllocArray[9] = "PIP_3.VS"
AllocArray[10] = "PIP_1.InpMemA"
AllocArray[11] = "PIP_1.HS"
AllocArray[12] = "PIP_1.InpMemB"
AllocArray[13] = "PIP_2.OpDisp"
AllocArray[14] = "PIP_3.HS"
AllocArray[15] = "PIP_2.VS"
AllocArray[16] = "PIP_2.JUG1"
AllocArray[17] = "PIP_2.JUG2"
AllocArray[18] = "PIP_2.MEM"
AllocArray[19] = "PIP_3.JUG2"
AllocArray[20] = "PIP_1.JUG2"
AllocArray[21] = "PIP_1.MEM"
AllocArray[22] = "PIP_1.OpDisp"
AllocArray[23] = "PIP_3.InpMemB"
AllocArray[24] = "PIP_3.JUG1"

AllocJSONString = json.dumps(AllocArray, sort_keys = False, indent = 4)

with open("ExampleAllocMap.json", "w") as JSONFile:
    JSONFile.write(AllocJSONString)

