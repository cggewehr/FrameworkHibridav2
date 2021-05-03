import PlatformComposer

# Creates base 5x4 NoC
SetupAB36 = PlatformComposer.Platform(BaseNoCDimensions=(5, 4))

# Adds Crossbar containing 4 PEs @ base NoC position (2, 0)
CrossbarA = PlatformComposer.Crossbar(AmountOfPEs = 4)
SetupAB36.addStructure(NewStructure=CrossbarA, WrapperLocationInBaseNoC=(2, 0))

# Adds Bus containing 6 PEs @ base NoC position (4, 0)
BusA = PlatformComposer.Bus(AmountOfPEs = 6)
SetupAB36.addStructure(NewStructure=BusA, WrapperLocationInBaseNoC=(4, 0))

# Adds Bus containing 6 PEs @ base NoC position (0, 3)
BusB = PlatformComposer.Bus(AmountOfPEs = 6)
SetupAB36.addStructure(NewStructure=BusB, WrapperLocationInBaseNoC=(0, 3))

# Adds Crossbar containing 4 PEs @ base NoC position (2, 3)
CrossbarB = PlatformComposer.Crossbar(AmountOfPEs = 4)
SetupAB36.addStructure(NewStructure=CrossbarB, WrapperLocationInBaseNoC=(2, 3))

SetupAB36.toJSON(SaveToFile = True, FileName = "SetupAB36")
