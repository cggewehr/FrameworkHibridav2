import sys
import PlatformComposer

# Creates base 3x3 NoC
Setup = PlatformComposer.Platform(BaseNoCDimensions=(3, 3), ReferenceClock=100)

# Adds crossbar containing 7 PEs @ base NoC position (2, 0)
CrossbarA = PlatformComposer.Crossbar(AmountOfPEs = 7)
Setup.addStructure(NewStructure=CrossbarA, WrapperLocationInBaseNoC=(2, 0))

# Adds bus containing 6 PEs @ base NoC position (2, 1)
BusA = PlatformComposer.Bus(AmountOfPEs = 6)
Setup.addStructure(NewStructure=BusA, WrapperLocationInBaseNoC=(2, 1))

# Adds bus containing 6 PEs @ base NoC position (2, 2)
BusB = PlatformComposer.Bus(AmountOfPEs = 6)
Setup.addStructure(NewStructure=BusB, WrapperLocationInBaseNoC=(2, 2))

Setup.updatePEAddresses()

print(str(BusA))
print(str(BusB))
print(str(CrossbarA))

print(str(Setup))

print("Reconstructing from JSON\n")

Setup.toJSON(SaveToFile = True, FileName = "H16_25")

JSONFile = open("H16_25.json")

SetupFromJSON = PlatformComposer.Platform(BaseNoCDimensions=(3, 3), ReferenceClock=100)
SetupFromJSON.fromJSON(JSONFile.read())

print(str(SetupFromJSON))

SetupFromJSON.toJSON(SaveToFile = True, FileName = "H16_25_fromJSON")
