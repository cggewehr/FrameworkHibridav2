import os
import AppComposer

# Makes a new Workload for each DVFS App made by "generateDVFSApps" from a given base Workload
def generateDVFSWorkloads(Workload, PlatformName):
    
    # Open new base Workload
    BaseWorkload = AppComposer.Workload()
    BaseWorkload.fromJSON(Workload)
    
    # Try to open Router-grained DVFS Application file
    try:
    
        # Open Router-grained DVFS Application file
        with open("../applications/DVFSAppRouterGrained" + str(PlatformName) + ".json", "r") as RouterGrainedFile:

            # Open new base Workload
            BaseWorkload = AppComposer.Workload()
            BaseWorkload.fromJSON(Workload)
        
            # Reads Application from JSON
            DVFSAppRouterGrained = AppComposer.Application()
            DVFSAppRouterGrained.fromJSON(RouterGrainedFile.read())
            
            # Add DVFSAppRouterGrained to BaseWorkload
            BaseWorkload.addApplication(DVFSAppRouterGrained)
            
            # Export Workload to JSON
            BaseWorkload.toJSON(SaveToFile = True, FileName = "DVFSWorkloadRouterGrained" + str(PlatformName))
            
    except (IOError, FileNotFoundError):
        print("Warning: Problem with file <../applications/DVFSAppRouterGrained" + str(PlatformName) + ".json>. Ignoring it")
        
    # Try to open Struct-grained DVFS Application file
    try:
    
        # Open Struct-grained DVFS Application file
        with open("../applications/DVFSAppStructGrained" + str(PlatformName) + ".json", "r") as StructGrainedFile:
        
            # Open new base Workload
            BaseWorkload = AppComposer.Workload()
            BaseWorkload.fromJSON(Workload)

            # Reads Application from JSON
            DVFSAppStructGrained = AppComposer.Application()
            DVFSAppStructGrained.fromJSON(StructGrainedFile.read())
            
            # Add DVFSAppRouterGrained to BaseWorkload
            BaseWorkload.addApplication(DVFSAppStructGrained)
            
            # Export Workload to JSON
            BaseWorkload.toJSON(SaveToFile = True, FileName = "DVFSWorkloadStructGrained" + str(PlatformName))
            
    except (IOError, FileNotFoundError):
        print("Warning: Problem with file <../applications/DVFSAppStructGrained" + str(PlatformName) + ".json>. Ignoring it")
        
    # Try to open Global-grained DVFS Application file
    try:
    
        # Open Global-grained DVFS Application file
        with open("../applications/DVFSAppGlobalGrained" + str(PlatformName) + ".json", "r") as GlobalGrainedFile:
                
            # Open new base Workload
            BaseWorkload = AppComposer.Workload()
            BaseWorkload.fromJSON(Workload)

            # Reads Application from JSON
            DVFSAppGlobalGrained = AppComposer.Application()
            DVFSAppGlobalGrained.fromJSON(GlobalGrainedFile.read())
            
            # Add DVFSAppRouterGrained to BaseWorkload
            BaseWorkload.addApplication(DVFSAppGlobalGrained)
            
            # Export Workload to JSON
            BaseWorkload.toJSON(SaveToFile = True, FileName = "DVFSWorkloadGlobalGrained" + str(PlatformName))
            
    except (IOError, FileNotFoundError):
        print("Warning: Problem with file <../applications/DVFSAppGlobalGrained" + str(PlatformName) + ".json>. Ignoring it")
        
    # Try to open Static-clocked DVFS Application file
    try:
    
        # Open Static-clocked DVFS Application file
        with open("../applications/DVFSAppStaticClocked" + str(PlatformName) + ".json", "r") as StaticClockedFile:
                        
            # Open new base Workload
            BaseWorkload = AppComposer.Workload()
            BaseWorkload.fromJSON(Workload)

            # Reads Application from JSON
            DVFSAppStaticClocked = AppComposer.Application()
            DVFSAppStaticClocked.fromJSON(StaticClockedFile.read())
            
            # Add DVFSAppRouterGrained to BaseWorkload
            BaseWorkload.addApplication(DVFSAppStaticClocked)
            
            # Export Workload to JSON
            BaseWorkload.toJSON(SaveToFile = True, FileName = "DVFSWorkloadStaticClocked" + str(PlatformName))
            
    except (IOError, FileNotFoundError):
        print("Warning: Problem with file <../applications/DVFSAppStaticClocked" + str(PlatformName) + ".json>. Ignoring it")
        
    # Try to open NoDVFS Application file
    try:
    
        # Open Static-clocked DVFS Application file
        with open("../applications/DVFSAppNoDVFS" + str(PlatformName) + ".json", "r") as StaticClockedFile:
                        
            # Open new base Workload
            BaseWorkload = AppComposer.Workload()
            BaseWorkload.fromJSON(Workload)

            # Reads Application from JSON
            DVFSAppNoDVFS = AppComposer.Application()
            DVFSAppNoDVFS.fromJSON(StaticClockedFile.read())
            
            # Add DVFSAppRouterGrained to BaseWorkload
            BaseWorkload.addApplication(DVFSAppNoDVFS)
            
            # Export Workload to JSON
            BaseWorkload.toJSON(SaveToFile = True, FileName = "DVFSWorkloadNoDVFS" + str(PlatformName))
            
    except (IOError, FileNotFoundError):
        print("Warning: Problem with file <../applications/DVFSAppNoDVFS" + str(PlatformName) + ".json>. Ignoring it")
        
if __name__ == "__main__":

    with open("./SwitchingWorkload.json", "r") as SwitchingWorkloadFile:
    
        SwitchingWorkloadAsJSON = SwitchingWorkloadFile.read()
    
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "SetupBB36")
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "SetupBA36")
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "SetupAB36")
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "SetupAA36")
        generateDVFSWorkloads(SwitchingWorkloadAsJSON, "Hermes36")
