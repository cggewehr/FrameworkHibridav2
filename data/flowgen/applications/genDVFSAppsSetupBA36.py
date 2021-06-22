import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [48, 32, 16, 0, 48, 32, 16, 7.23, 16, 24, 12.215, 11.84, 40, 24, 12.215, 23.25]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [0, 0, 0, 0, 14.46, 0, 0, 14.46, 22.5, 24.4275, 24.4275, 22.5, 46.2474, 24.4275, 24.4275, 46.2475]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [90.5, 90.5, 102.75, 12.25, 27.625, 93.25, 88.25, 18.125, 12.5, 88.25, 200, 12.5, 12.5, 105.75, 148.5, 12.5]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [16, 32, 16, 0, 32.125, 32, 16, 14.46, 12.5, 48, 24.4275, 23.6775, 12.5, 10, 24.4275, 46.4975]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequenciesBB = [80, 13.015]  # Workload BB, frequency in MHz
BusClockFrequenciesMM = [26.03, 26.03]  # Workload MM, frequency in MHz
BusClockFrequenciesAA = [37.75, 24.25]  # Workload AA, frequency in MHz
BusClockFrequenciesHH = [48.25, 26.03] # Workload HH, frequency in MHz
BusClockFrequencies = [BusClockFrequenciesBB, BusClockFrequenciesMM, BusClockFrequenciesAA, BusClockFrequenciesHH]

CrossbarClockFrequenciesBB = [48, 75]  # Workload BB, frequency in MHz
CrossbarClockFrequenciesMM = [150, 150]  # Workload MM, frequency in MHz
CrossbarClockFrequenciesAA = [230.375, 230.375]  # Workload AA, frequency in MHz
CrossbarClockFrequenciesHH = [230.375, 150] # Workload HH, frequency in MHz
CrossbarClockFrequencies = [CrossbarClockFrequenciesBB, CrossbarClockFrequenciesMM, CrossbarClockFrequenciesAA, CrossbarClockFrequenciesHH]

# Open SetupBA36 JSON file
with open("../topologies/SetupBA36.json", "r") as BA36File:
    
    # Get Platform object from JSON 
    SetupBA36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    SetupBA36.fromJSON(BA36File.read())
    
    # Sets counter resolutions values
    CounterResolutions = [32, 24, 16, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    
    # Generate DVFS apps for each counter resolution (but same computed clock frequencies at minimum granularity)
    for res in CounterResolutions:
        print("Generating DVFS Application for Topology <" + "SetupBA36" + "> with counter resolution <" + str(res) + ">")
        SetupBA36.DVFSCounterResolution = res
        generateDVFSApps(Platform = SetupBA36, PlatformName = "SetupBA36", RouterClockFrequencies = RouterClockFrequencies, BusClockFrequencies = BusClockFrequencies, CrossbarClockFrequencies = CrossbarClockFrequencies)
