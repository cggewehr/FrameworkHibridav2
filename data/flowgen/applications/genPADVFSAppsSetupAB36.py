import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [48,24,48,40,48,16,48,48,24,48,16,24.4275,24.4275,75,48,45,45,75,75,0]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [0,150,150,90,90,0,150,24.4275,24.4275,0,0,24.4275,24.4275,150,0,90,90,150,150,0]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [17.5,230.375,230.375,230.375,224.125,90.5,102.75,90.75,200,200,90.5,102.75,102.75,105.75,200,224.125,230.375,230.375,230.375,90.75]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [48,150,150,90,90,48,150,24.4275,24.4275,16,48,16,32,32,32,224.125,230.375,230.375,230.375,0]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequenciesBB = [48, 45]  # Workload BB, frequency in MHz
BusClockFrequenciesMM = [90, 90]  # Workload MM, frequency in MHz
BusClockFrequenciesAA = [224.125, 224.125]  # Workload AA, frequency in MHz
BusClockFrequenciesHH = [90, 224.125] # Workload HH, frequency in MHz
BusClockFrequencies = [BusClockFrequenciesBB, BusClockFrequenciesMM, BusClockFrequenciesAA, BusClockFrequenciesHH]

CrossbarClockFrequenciesBB = [48, 75]  # Workload BB, frequency in MHz
CrossbarClockFrequenciesMM = [150, 150]  # Workload MM, frequency in MHz
CrossbarClockFrequenciesAA = [230.375, 230.375]  # Workload AA, frequency in MHz
CrossbarClockFrequenciesHH = [150, 230.375] # Workload HH, frequency in MHz
CrossbarClockFrequencies = [CrossbarClockFrequenciesBB, CrossbarClockFrequenciesMM, CrossbarClockFrequenciesAA, CrossbarClockFrequenciesHH]

# Open SetupAB36 JSON file
with open("../topologies/SetupAB36.json", "r") as AB36File:
    
    # Get Platform object from JSON 
    SetupAB36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    SetupAB36.fromJSON(AB36File.read())
    
    # Sets counter resolutions values
    CounterResolutions = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    
    # Generate DVFS apps for each counter resolution (but same computed clock frequencies at minimum granularity)
    for res in CounterResolutions:
        print("Generating DVFS Application for Topology <" + "SetupAB36" + "> with counter resolution <" + str(res) + ">")
        SetupAB36.DVFSCounterResolution = res
        generateDVFSApps(Platform = SetupAB36, PlatformName = "PASetupAB36", RouterClockFrequencies = RouterClockFrequencies, BusClockFrequencies = BusClockFrequencies, CrossbarClockFrequencies = CrossbarClockFrequencies)
