import PlatformComposer

# Creates base 4x4 NoC
SetupBA36 = PlatformComposer.Platform(BaseNoCDimensions=(4, 4))

# Adds Bus containing 4 PEs @ base NoC position (0, 1)
BusA = PlatformComposer.Bus(AmountOfPEs = 4)
SetupBA36.addStructure(NewStructure=BusA, WrapperLocationInBaseNoC=(0, 1))

# Adds Bus containing 4 PEs @ base NoC position (3, 1)
BusB = PlatformComposer.Bus(AmountOfPEs = 4)
SetupBA36.addStructure(NewStructure=BusB, WrapperLocationInBaseNoC=(3, 1))

# Adds Crossbar containing 8 PEs @ base NoC position (2, 0)
CrossbarA = PlatformComposer.Crossbar(AmountOfPEs = 8)
SetupBA36.addStructure(NewStructure=CrossbarA, WrapperLocationInBaseNoC=(2, 0))

# Adds Crossbar containing 8 PEs @ base NoC position (2, 3)
CrossbarB = PlatformComposer.Crossbar(AmountOfPEs = 8)
SetupBA36.addStructure(NewStructure=CrossbarB, WrapperLocationInBaseNoC=(2, 3))

SetupBA36.toJSON(SaveToFile = True, FileName = "SetupBA36")
