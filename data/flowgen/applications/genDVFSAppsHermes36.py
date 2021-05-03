import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [3.695, 3.215, 16, 16, 32, 48, 7.07, 500, 5.14, 5.14, 5.14, 56.56, 90, 12.215, 12.215, 24, 40, 16, 22.5, 45, 23.785, 24, 48, 32, 30, 75, 30, 24, 48, 24, 25.7125, 45, 0, 16, 24, 24]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [7.39, 6.43, 0, 0, 6.43, 7.39, 14.14, 1.285, 1.285, 1.285, 1.285, 22.5, 45, 90, 47.57, 47.57, 90, 45, 60, 150, 60, 60, 150, 60, 30, 90, 0, 0, 90, 30]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [0.0626, 26.625, 62.5, 0.0625, 26.625, 0.0625, 125, 230.375, 0.0625, 125, 230.375, 23.75, 224.0625, 197.5, 10, 80, 12.5, 10, 80, 12.5, 8, 200, 148.5, 12.25, 90.5, 90.5, 105.75, 88.25, 93.25, 97.25, 102.75, 17.5]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [7.39, 6.43, 16, 16, 32, 48, 14.14, 1.285, 16, 32, 16, 16, 22.5, 25.4275, 24.4275, 24, 40, 15, 45, 90, 47.57, 24, 48, 32, 60, 150, 60, 24, 48, 24, 40, 90, 0, 16, 24, 24]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequencies = None

CrossbarClockFrequencies = None

# Open Hermes36 JSON file
with open("../topologies/Hermes36.json", "r") as Hermes36File:
    
    # Get Platform object from JSON 
    Hermes36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    Hermes36.fromJSON(Hermes36File.read())
    
    # Generate DVFS apps
    generateDVFSApps(Platform = Hermes36, PlatformName = "Hermes36", RouterClockFrequencies, BusClockFrequencies, CrossbarClockFrequencies)
