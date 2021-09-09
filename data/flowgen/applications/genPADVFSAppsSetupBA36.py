import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [48,48,16,0,80,32,32,13.015,48,40,45,45,48,40,45,45]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [0,0,0,0,26.03,0,0,26.03,22.5,46.1775,46.1775,22.5,46.1775,46.1775,46.1775,46.1775]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [90.5,90.5,102.75,97.25,224.0625,95.75,97.25,224.0625,224.0625,200,200,224.0625,224.0625,105.75,200,224.0625]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [32,32,32,0,224.0625,224.0625,16,26.03,224.0625,224.0625,46.1775,22.5,224.0625,224.0625,46.1775,46.1775]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequenciesBB = [80, 13.015]  # Workload BB, frequency in MHz
BusClockFrequenciesMM = [26.03, 26.03]  # Workload MM, frequency in MHz
BusClockFrequenciesAA = [224.0625, 224.0625]  # Workload AA, frequency in MHz
BusClockFrequenciesHH = [224.0625, 26.03] # Workload HH, frequency in MHz
BusClockFrequencies = [BusClockFrequenciesBB, BusClockFrequenciesMM, BusClockFrequenciesAA, BusClockFrequenciesHH]

CrossbarClockFrequenciesBB = [48, 75]  # Workload BB, frequency in MHz
CrossbarClockFrequenciesMM = [200, 200]  # Workload MM, frequency in MHz
CrossbarClockFrequenciesAA = [230.375, 230.375]  # Workload AA, frequency in MHz
CrossbarClockFrequenciesHH = [230.375, 200] # Workload HH, frequency in MHz
CrossbarClockFrequencies = [CrossbarClockFrequenciesBB, CrossbarClockFrequenciesMM, CrossbarClockFrequenciesAA, CrossbarClockFrequenciesHH]

# Open SetupBA36 JSON file
with open("../topologies/SetupBA36.json", "r") as BA36File:
    
    # Get Platform object from JSON 
    SetupBA36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    SetupBA36.fromJSON(BA36File.read())
    
    # Sets counter resolutions values
    CounterResolutions = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    
    # Generate DVFS apps for each counter resolution (but same computed clock frequencies at minimum granularity)
    for res in CounterResolutions:
        print("Generating DVFS Application for Topology <" + "SetupBA36" + "> with counter resolution <" + str(res) + ">")
        SetupBA36.DVFSCounterResolution = res
        generateDVFSApps(Platform = SetupBA36, PlatformName = "PASetupBA36", RouterClockFrequencies = RouterClockFrequencies, BusClockFrequencies = BusClockFrequencies, CrossbarClockFrequencies = CrossbarClockFrequencies)
