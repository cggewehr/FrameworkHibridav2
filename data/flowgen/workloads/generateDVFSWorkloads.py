import os
import AppComposer

# Makes a new Workload for each DVFS App made by "generateDVFSApps" from a given base Workload
def generateDVFSWorkloads(Workload, PlatformName, CounterResolutions):
    
    # Open new base Workload
    BaseWorkload = AppComposer.Workload()
    BaseWorkload.fromJSON(Workload)

    for res in CounterResolutions:    

        # Try to open Router-grained DVFS Application file
        try:
        
            # Open Router-grained DVFS Application file
            with open("../applications/" + PlatformName + "/DVFSAppRouterGrained" + str(PlatformName) + "Resolution" + str(res) + ".json", "r") as RouterGrainedFile:

                # Open new base Workload
                BaseWorkload = AppComposer.Workload()
                BaseWorkload.fromJSON(Workload)
            
                # Reads Application from JSON
                DVFSAppRouterGrained = AppComposer.Application()
                DVFSAppRouterGrained.fromJSON(RouterGrainedFile.read())
                
                # Add DVFSAppRouterGrained to BaseWorkload
                BaseWorkload.addApplication(DVFSAppRouterGrained)
                
                # Export Workload to JSON
                BaseWorkload.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSWorkloadRouterGrained" + str(PlatformName) + "Resolution" + str(res))
                
        except (IOError, FileNotFoundError):
            print("Warning: Problem with file <../applications/" + PlatformName + "/DVFSAppRouterGrained" + str(PlatformName) + "Resolution" + str(res) + ".json>. Ignoring it")
            
        # Try to open Struct-grained DVFS Application file
        try:
        
            # Open Struct-grained DVFS Application file
            with open("../applications/" + PlatformName + "/DVFSAppStructGrained" + str(PlatformName) + "Resolution" + str(res) + ".json", "r") as StructGrainedFile:
            
                # Open new base Workload
                BaseWorkload = AppComposer.Workload()
                BaseWorkload.fromJSON(Workload)

                # Reads Application from JSON
                DVFSAppStructGrained = AppComposer.Application()
                DVFSAppStructGrained.fromJSON(StructGrainedFile.read())
                
                # Add DVFSAppRouterGrained to BaseWorkload
                BaseWorkload.addApplication(DVFSAppStructGrained)
                
                # Export Workload to JSON
                BaseWorkload.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSWorkloadStructGrained" + str(PlatformName) + "Resolution" + str(res))
            
        except (IOError, FileNotFoundError):
            print("Warning: Problem with file <../applications/" + PlatformName + "/DVFSAppStructGrained" + str(PlatformName) + "Resolution" + str(res) + ".json>. Ignoring it")
            
        # Try to open Global-grained DVFS Application file
        try:
        
            # Open Global-grained DVFS Application file
            with open("../applications/" + PlatformName + "/DVFSAppGlobalGrained" + str(PlatformName) + "Resolution" + str(res) + ".json", "r") as GlobalGrainedFile:
                    
                # Open new base Workload
                BaseWorkload = AppComposer.Workload()
                BaseWorkload.fromJSON(Workload)

                # Reads Application from JSON
                DVFSAppGlobalGrained = AppComposer.Application()
                DVFSAppGlobalGrained.fromJSON(GlobalGrainedFile.read())
                
                # Add DVFSAppRouterGrained to BaseWorkload
                BaseWorkload.addApplication(DVFSAppGlobalGrained)
                
                # Export Workload to JSON
                BaseWorkload.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSWorkloadGlobalGrained" + str(PlatformName) + "Resolution" + str(res))
                
        except (IOError, FileNotFoundError):
            print("Warning: Problem with file <../applications/" + PlatformName + "/DVFSAppGlobalGrained" + str(PlatformName) + "Resolution" + str(res) + ".json>. Ignoring it")
            
        # Try to open Static-clocked DVFS Application file
        try:
        
            # Open Static-clocked DVFS Application file
            with open("../applications/" + PlatformName + "/DVFSAppStaticClocked" + str(PlatformName) + "Resolution" + str(res) + ".json", "r") as StaticClockedFile:
                            
                # Open new base Workload
                BaseWorkload = AppComposer.Workload()
                BaseWorkload.fromJSON(Workload)

                # Reads Application from JSON
                DVFSAppStaticClocked = AppComposer.Application()
                DVFSAppStaticClocked.fromJSON(StaticClockedFile.read())
                
                # Add DVFSAppRouterGrained to BaseWorkload
                BaseWorkload.addApplication(DVFSAppStaticClocked)
                
                # Export Workload to JSON
                BaseWorkload.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSWorkloadStaticClocked" + str(PlatformName) + "Resolution" + str(res))
                
        except (IOError, FileNotFoundError):
            print("Warning: Problem with file <../applications/" + PlatformName + "/DVFSAppStaticClocked" + str(PlatformName) + "Resolution" + str(res) + ".json>. Ignoring it")
        
    # Try to open NoDVFS Application file
    try:
    
        # Open No-DVFS Application file
        with open("../applications/" + PlatformName + "/DVFSAppNoDVFS" + str(PlatformName) + ".json", "r") as StaticClockedFile:
                        
            # Open new base Workload
            BaseWorkload = AppComposer.Workload()
            BaseWorkload.fromJSON(Workload)

            # Reads Application from JSON
            DVFSAppNoDVFS = AppComposer.Application()
            DVFSAppNoDVFS.fromJSON(StaticClockedFile.read())
            
            # Add DVFSAppRouterGrained to BaseWorkload
            BaseWorkload.addApplication(DVFSAppNoDVFS)
            
            # Export Workload to JSON
            BaseWorkload.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSWorkloadNoDVFS" + str(PlatformName))
            
    except (IOError, FileNotFoundError):
        print("Warning: Problem with file <../applications/" + PlatformName + "/DVFSAppNoDVFS" + str(PlatformName) + ".json>. Ignoring it")
        
if __name__ == "__main__":

    with open("./SwitchingWorkload.json", "r") as SwitchingWorkloadFile:
    
        SwitchingWorkloadAsJSON = SwitchingWorkloadFile.read()

        CounterResolutions = [32, 24, 16, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "SetupBB36", CounterResolutions)
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "SetupBA36", CounterResolutions)
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "SetupAB36", CounterResolutions)
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "SetupAA36", CounterResolutions)
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "Hermes36", CounterResolutions)
