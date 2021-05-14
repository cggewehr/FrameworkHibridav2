import PlatformComposer

# Creates base 6x6 NoC
SetupBB36 = PlatformComposer.Platform(BaseNoCDimensions=(6, 6), DVFSEnable = True)

SetupBB36.toJSON(SaveToFile = True, FileName = "Hermes36")
