import json

# AllocMap[PEPos] = App.Thread
AllocArray = [None] * 100
AllocArray[0] = "DummyThreadA"
AllocArray[1] = "DummyThreadB"

AllocJSONString = json.dumps(AllocArray, sort_keys = False, indent = 4)

with open("dummyAllocMap.json", "w") as JSONFile:
    JSONFile.write(AllocJSONString)
