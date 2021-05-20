import PlatformComposer

# Creates base 4x4 NoC
SetupAA36 = PlatformComposer.Platform(BaseNoCDimensions=(4, 4))

# Adds Crossbar containing 7 PEs @ base NoC position (3, 0)
CrossbarA = PlatformComposer.Crossbar(AmountOfPEs = 7)
SetupAA36.addStructure(NewStructure=CrossbarA, WrapperLocationInBaseNoC=(3, 0))

# Adds Crossbar containing 8 PEs @ base NoC position (0, 3)
CrossbarB = PlatformComposer.Crossbar(AmountOfPEs = 8)
SetupAA36.addStructure(NewStructure=CrossbarB, WrapperLocationInBaseNoC=(0, 3))

# Adds Crossbar containing 8 PEs @ base NoC position (3, 3)
CrossbarC = PlatformComposer.Crossbar(AmountOfPEs = 8)
SetupAA36.addStructure(NewStructure=CrossbarC, WrapperLocationInBaseNoC=(3, 3))

SetupAA36.toJSON(SaveToFile = True, FileName = "SetupAA36")
