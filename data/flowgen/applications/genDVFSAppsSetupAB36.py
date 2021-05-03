import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [24, 24, 48, 24, 32, 24, 48, 24, 24, 32, 16, 12.125, 12.125, 25.7125, 32, 22.66, 23.785, 75, 30, 0]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [0, 60, 150, 90, 45.32, 0, 30, 24.4275, 24.4275, 0, 0, 24.4275, 24.4275, 30, 0, 45.32, 90, 150, 60, 0]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [17.5, 62.5, 183.25, 120.75, 58.25, 90.5, 12.25, 90.75, 88.25, 200, 90.5, 102.75, 97.25, 105.75, 148.5, 58.25, 120.75, 183.25, 62.5, 8]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [48, 60, 150, 90, 45.32, 32, 30, 24.4275, 24.4275, 16, 16, 16, 32, 32, 32, 58.25, 120.75, 183.25, 62.5, 0]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequenciesBB = [112, 46.765]  # Workload BB, frequency in MHz
BusClockFrequenciesMM = [93.53, 93.53]  # Workload MM, frequency in MHz
BusClockFrequenciesAA = [134, 134]  # Workload AA, frequency in MHz
BusClockFrequenciesHH = [93.53, 134] # Workload HH, frequency in MHz
BusClockFrequencies = [BusClockFrequenciesBB, BusClockFrequenciesMM, BusClockFrequenciesAA, BusClockFrequenciesHH]

CrossbarClockFrequenciesBB = [48, 75]  # Workload BB, frequency in MHz
CrossbarClockFrequenciesMM = [150, 150]  # Workload MM, frequency in MHz
CrossbarClockFrequenciesAA = [230.375, 230.275]  # Workload AA, frequency in MHz
CrossbarClockFrequenciesHH = [150, 230.375] # Workload HH, frequency in MHz
CrossbarClockFrequencies = [CrossbarClockFrequenciesBB, CrossbarClockFrequenciesMM, CrossbarClockFrequenciesAA, CrossbarClockFrequenciesHH]

# Open SetupAB36 JSON file
with open("../topologies/SetupAB36.json", "r") as AB36File:
    
    # Get Platform object from JSON 
    SetupAB36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    SetupAB36.fromJSON(AB36File.read())
    
    # Generate DVFS apps
    generateDVFSApps(Platform = SetupAB36, PlatformName = "SetupAB36", RouterClockFrequencies, BusClockFrequencies, CrossbarClockFrequencies)
