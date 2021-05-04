import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [48, 32, 0, 45, 15, 16, 16, 30, 75, 30, 48, 24, 32, 45, 23.625, 48, 24, 48, 23.785, 12.215, 24, 24, 24, 48, 16]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [30, 51.4275, 0, 24.4275, 24.4275, 90, 150, 0, 90, 47.57, 22.82, 90, 0, 22.5, 22.82, 47.57, 90, 0, 150, 90, 24.4275, 24.4275, 0, 51.2475, 30]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [197.5, 230.375, 62.5, 230.375, 197.5, 224.125, 115.375, 62.5, 84.125, 224.125, 63, 80, 12.25, 80, 71, 17.5, 102.75, 72.5, 98.25, 148.5, 90.5, 90.5, 93.25, 88.25, 200]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [197.5, 230.375, 62.5, 90, 30, 224.125, 115.375, 60, 150, 60, 63, 80, 0, 30, 47.25, 48, 16, 16, 47.57, 23.6775, 32, 16, 16, 32, 16]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequenciesBB = [24, 17.75875]  # Workload BB, frequency in MHz
BusClockFrequenciesMM = [23.3025, 23.3025]  # Workload MM, frequency in MHz
BusClockFrequenciesAA = [36.5, 38.5]  # Workload AA, frequency in MHz
BusClockFrequenciesHH = [36.5, 35.5175] # Workload HH, frequency in MHz
BusClockFrequencies = [BusClockFrequenciesBB, BusClockFrequenciesMM, BusClockFrequenciesAA, BusClockFrequenciesHH]

CrossbarClockFrequencies = None

# Open SetupBB36 JSON file
with open("../topologies/SetupBB36.json", "r") as BB36File:
    
    # Get Platform object from JSON 
    SetupBB36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    SetupBB36.fromJSON(BB36File.read())
    
    # Generate DVFS apps
    generateDVFSApps(Platform = SetupBB36, PlatformName = "SetupBB36", RouterClockFrequencies = RouterClockFrequencies, BusClockFrequencies = BusClockFrequencies, CrossbarClockFrequencies = CrossbarClockFrequencies)
