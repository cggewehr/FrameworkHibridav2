import os
import AppComposer

# Makes a new Workload for each DVFS App made by "generateDVFSApps" from a given base Workload
def AddDVFSApp(Setup, Resolution, Granularity, Workload, FileName):
    
    # Open DVFS Application
    #with open("../applications/" + PlatformName + "/DVFSAppRouterGrained" + str(PlatformName) + "Resolution" + str(res) + ".json", "r") as DVFSAppFile:
    with open("../applications/" + FileName + ".json", "r") as DVFSAppFile:
        DVFSApp = AppComposer.Application().fromJSON(DVFSAppFile.read())

    # Open base Workload
    with open(Workload + ".json", "r") as WorkloadFile:
        Workload = AppComposer.Workload().fromJSON(WorkloadFile.read())
    
    # Add DVFS App to Workload
    Workload.addApplication(DVFSApp)
    
    # Export Workload to JSON with DVFS App added
    Workload.toJSON(SaveToFile = True, FileName = FileName)


if __name__ == "__main__":

    Setups = ["SetupBB36", "SetupBA36", "SetupAB36", "SetupAA36", "Hermes36"]
    CounterResolutions = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    Granularities = ["GlobalGrained", "StructGrained", "RouterGrained"]
    Workloads = ["WorkloadBB", "WorkloadMM", "WorkloadAA", "WorkloadHH"]

    for Setup in Setups:
        for Resolution in CounterResolutions:
            for Granularity in Granularities:

                if Setup == "Hermes36" and Granularity == "StructGrained":
                    continue

                for Workload in Workloads:

                    FileName = Workload + "/" + Setup + "_" + str(Resolution) + "_" + Granularity + "_" + Workload
                    AddDVFSApp(Setup, Resolution, Granularity, Workload, FileName)                    

    # Add NoDVFS App
    for Setup in Setups:
        for Workload in Workloads:

            FileName = Workload + "/" + Setup + "_" + "NoDVFS" + "_" + Workload
            AddDVFSApp(Setup, Resolution, Granularity, Workload, FileName)
