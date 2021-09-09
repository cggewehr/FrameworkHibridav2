import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [48, 48, 0, 45, 75, 96, 16, 75, 75, 75, 48, 24, 48, 75, 45, 96, 24, 48, 45, 81.1075, 24, 24, 24, 40, 40]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [150,150,0,24.4275,24.4275,150,150,0,150,90,90,90,0,90,90,90,150,0,150,150,24.4275,24.4275,0,150,150]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [230.375,230.375,230.375,230.375,230.375,224.125,230.375,230.375,230.375,224.125,224.125,224.125,102.75,224.125,224.125,17.5,102.75,72.5,148.5,148.5,90.5,90.5,93.25,88.25,200]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [230.375,230.375,230.375,90,150,224.125,230.375,150,150,150,224.125,224.125,0,150,90,48,48,16,90,23.6775,48,32,32,32,16]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequenciesBB = [96, 81.1075]  # Workload BB, frequency in MHz
BusClockFrequenciesMM = [90, 90]  # Workload MM, frequency in MHz
BusClockFrequenciesAA = [224.125, 224.125]  # Workload AA, frequency in MHz
BusClockFrequenciesHH = [224.125, 90] # Workload HH, frequency in MHz
BusClockFrequencies = [BusClockFrequenciesBB, BusClockFrequenciesMM, BusClockFrequenciesAA, BusClockFrequenciesHH]

CrossbarClockFrequencies = None

# Open SetupBB36 JSON file
with open("../topologies/SetupBB36.json", "r") as BB36File:
    
    # Get Platform object from JSON 
    SetupBB36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    SetupBB36.fromJSON(BB36File.read())
    
    # Sets counter resolutions values
    CounterResolutions = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    
    # Generate DVFS apps for each counter resolution (but same computed clock frequencies at minimum granularity)
    for res in CounterResolutions:
        print("Generating DVFS Application for Topology <" + "SetupBB36" + "> with counter resolution <" + str(res) + ">")
        SetupBB36.DVFSCounterResolution = res
        generateDVFSApps(Platform = SetupBB36, PlatformName = "PASetupBB36", RouterClockFrequencies = RouterClockFrequencies, BusClockFrequencies = BusClockFrequencies, CrossbarClockFrequencies = CrossbarClockFrequencies)
