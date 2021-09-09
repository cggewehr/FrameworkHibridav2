import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [24,0,16,16,24,16,23.785,3.535,16,3.215,3.695,23.09,40,12.215,23.09,23.09]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [0,0,0,11.57,24.4275,6.43,0,47.2475,24.4275,46.9275,2.57,47.2475,46.9275,46.9275,7.07,46.9275]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [105.75,105.75,200,200,230.375,17.5,93.25,88.25,230.375,230.375,230.375,230.375,230.375,160,160,230.375]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [7.07,2.57,16,16,22.5,14.14,0,230.375,24.4275,6.43,230.375,230.375,46.9275,24.4275,160,230.375]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequencies = None

CrossbarClockFrequenciesBB = [48, 48, 75]  # Workload BB, frequency in MHz
CrossbarClockFrequenciesMM = [11.57, 150, 150]  # Workload MM, frequency in MHz
CrossbarClockFrequenciesAA = [200, 230.375, 230.375]  # Workload AA, frequency in MHz
CrossbarClockFrequenciesHH = [48, 150, 230.375] # Workload HH, frequency in MHz
CrossbarClockFrequencies = [CrossbarClockFrequenciesBB, CrossbarClockFrequenciesMM, CrossbarClockFrequenciesAA, CrossbarClockFrequenciesHH]

# Open SetupAA36 JSON file
with open("../topologies/SetupAA36.json", "r") as AA36File:
    
    # Get Platform object from JSON 
    SetupAA36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    SetupAA36.fromJSON(AA36File.read())
    
    # Sets counter resolutions values
    CounterResolutions = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    
    # Generate DVFS apps for each counter resolution (but same computed clock frequencies at minimum granularity)
    for res in CounterResolutions:
        print("Generating DVFS Application for Topology <" + "SetupAA36" + "> with counter resolution <" + str(res) + ">")
        SetupAA36.DVFSCounterResolution = res
        generateDVFSApps(Platform = SetupAA36, PlatformName = "PASetupAA36", RouterClockFrequencies = RouterClockFrequencies, BusClockFrequencies = BusClockFrequencies, CrossbarClockFrequencies = CrossbarClockFrequencies)
