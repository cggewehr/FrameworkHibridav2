import PlatformComposer

# Creates base 5x5 NoC
SetupBB36 = PlatformComposer.Platform(BaseNoCDimensions=(5, 5), DVFSEnable = True)

# Adds bus containing 6 PEs @ base NoC position (0, 2)
BusA = PlatformComposer.Bus(AmountOfPEs = 6)
SetupBB36.addStructure(NewStructure=BusA, WrapperLocationInBaseNoC=(0, 2))

# Adds bus containing 7 PEs @ base NoC position (4, 2)
BusB = PlatformComposer.Bus(AmountOfPEs = 7)
SetupBB36.addStructure(NewStructure=BusB, WrapperLocationInBaseNoC=(4, 2))

SetupBB36.toJSON(SaveToFile = True, FileName = "SetupBB36")
