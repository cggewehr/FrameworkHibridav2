import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [24, 0, 16, 16, 24, 16, 1.285, 3.535, 24, 3.215, 3.695, 11.25, 24, 12.215, 12.215, 13.5]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [0, 0, 0, 22.82, 24.4275, 6.43, 0, 24.4275, 26.9975, 9, 2.57, 24.4275, 26.9975, 22.5, 7.07, 22.82]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [8, 12.25, 88.25, 191.5, 0.0625, 17.5, 93.25, 0.0625, 12.625, 5.0625, 5.0625, 12.625, 10.125, 12.5, 12.5, 10.125]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [7.07, 2.57, 16, 16, 22.5, 7.39, 0, 0.0625, 24.4275, 6.43, 5.0625, 12.625, 24.3975, 24.3975, 12.5, 10.125]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequencies = None

CrossbarClockFrequenciesBB = [48, 48, 75]  # Workload BB, frequency in MHz
CrossbarClockFrequenciesMM = [11.25, 150, 150]  # Workload MM, frequency in MHz
CrossbarClockFrequenciesAA = [200, 230.375, 230.375]  # Workload AA, frequency in MHz
CrossbarClockFrequenciesHH = [48, 150, 230.375] # Workload HH, frequency in MHz
CrossbarClockFrequencies = [CrossbarClockFrequenciesBB, CrossbarClockFrequenciesMM, CrossbarClockFrequenciesAA, CrossbarClockFrequenciesHH]

# Open SetupAA36 JSON file
with open("../topologies/SetupAA36.json", "r") as AA36File:
    
    # Get Platform object from JSON 
    SetupAA36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    SetupAA36.fromJSON(AA36File.read())
    
    # Generate DVFS apps
    generateDVFSApps(Platform = SetupAA36, PlatformName = "SetupAA36", RouterClockFrequencies = RouterClockFrequencies, BusClockFrequencies = BusClockFrequencies, CrossbarClockFrequencies = CrossbarClockFrequencies)
