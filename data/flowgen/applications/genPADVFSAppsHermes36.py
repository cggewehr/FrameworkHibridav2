import PlatformComposer
from generateDVFSApps import *

RouterClockFrequenciesBB = [7.23,3.215,32,16,48,48,7.07,23.785,23.785,32,32,48,11.25,12.215,23.785,40,48,40,45,75,45,24,48,48,75,75,75,48,48,24,75,45,0,16,16,48]  # Workload BB, frequency in MHz
RouterClockFrequenciesMM = [14.46,6.43,0,0,6.43,14.14,14.14,47.57,23.785,23.785,47.57,14.14,22.5,24.43,47.57,47.57,24.43,22.5,90,180,90,90,180,90,150,150,150,150,150,150,150,90,0,0,90,150]  # Workload MM, frequency in MHz
RouterClockFrequenciesAA = [224.0625,230.375,230.375,224.0625,230.375,230.375,224.0625,230.375,230.375,224.0625,230.375,230.375,224.0625,224.0625,230.375,224.0625,224.0625,230.375,224.0625,224.0625,224.0625,224.0625,224.0625,224.0625,93.25,200,200,102.75,90.5,90.5,105.75,200,93.25,102.75,102.75,17.5]  # Workload AA, frequency in MHz
RouterClockFrequenciesHH = [14.14,6.43,32,16,48,48,14.14,47.57,23.785,32,32,48,22.5,24.43,24.43,224.0625,230.375,230.375,90,180,90,224.0625,230.375,230.375,150,150,150,224.0625,224.0625,230.375,150,90,0,224.0625,224.0625,224.0625]  # Workload HH, frequency in MHz
RouterClockFrequencies = [RouterClockFrequenciesBB, RouterClockFrequenciesMM, RouterClockFrequenciesAA, RouterClockFrequenciesHH]

BusClockFrequencies = None

CrossbarClockFrequencies = None

# Open Hermes36 Topology JSON file
with open("../topologies/Hermes36.json", "r") as Hermes36File:
    
    # Get Platform object from JSON 
    Hermes36 = PlatformComposer.Platform(BaseNoCDimensions = (1,1))
    Hermes36.fromJSON(Hermes36File.read())

    # Sets counter resolutions values
    CounterResolutions = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    
    # Generate DVFS apps for each counter resolution (but same computed clock frequencies at minimum granularity)
    for res in CounterResolutions:
        print("Generating DVFS Application for Topology <" + "Hermes36" + "> with counter resolution <" + str(res) + ">")
        Hermes36.DVFSCounterResolution = res
        generateDVFSApps(Platform = Hermes36, PlatformName = "PAHermes36", RouterClockFrequencies = RouterClockFrequencies, BusClockFrequencies = BusClockFrequencies, CrossbarClockFrequencies = CrossbarClockFrequencies)
