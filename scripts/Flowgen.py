
import json
import os
import shutil
import sys

import PlatformComposer
import AppComposer

def flowgen(args):

    # Gets framework configs
    with open(os.getenv("HIBRIDA_CONFIG_FILE"), "r") as ConfigFile:
        ConfigDict = json.loads(ConfigFile.read())
        
    # Gets framework project index
    with open(ConfigDict["HibridaPath"] + "/projectIndex.json", "r") as ProjectIndexFile:
        ProjectIndexDict = json.loads(ProjectIndexFile.read())
    
    # Sets default project as MRU project
    if args.ProjectName is None:
        print("Warning: No project passed as target, using <" + ConfigDict["MostRecentProject"] + "> as default")
        args.ProjectName = ConfigDict["MostRecentProject"]
        
    # Checks if project exists
    if args.ProjectName not in ProjectIndexDict.keys():
        print("Error: Project <" + args.ProjectName + "> doesnt exist")
        exit(1)
        
    # Gets project dir
    ProjectDir = ProjectIndexDict[args.ProjectName]
    
    # Opens Allocation Map JSON file
    try:
        AllocMapFile = open(ProjectDir + "/src_json/AllocationMap.json", "r")
    except FileNotFoundError:
        print("Error: Allocation Map file not found. Please use the setConfig command to set an Allocation Map file")
        exit(1)
    except IOError:
        print("Error: Allocation Map file cant be opened")
        exit(1)
        
    # Opens Cluster Clocks JSON file
    try:
        ClusterClocksFile = open(ProjectDir + "/src_json/ClusterClocks.json", "r")
    except FileNotFoundError:
        print("Error: Cluster Clocks file not found. Please use the setConfig command to set a ClusterClocks file")
        exit(1)
    except IOError:
        print("Error: Cluster Clocks file cant be opened")
        exit(1)
        
    # Opens Topology JSON file
    try:
        TopologyFile = open(ProjectDir + "/src_json/Topology.json", "r")
    except FileNotFoundError:
        print("Error: Topology file not found. Please use the setConfig command to set a Topology file")
        exit(1)
    except IOError:
        print("Error: Topology file cant be opened")
        exit(1)
    
    # Opens Workload JSON file
    try:
        WorkloadFile = open(ProjectDir + "/src_json/Workload.json", "r")
    except FileNotFoundError:
        print("Error: Workload file not found. Please use the setConfig command to set a Workload file")
        exit(1)
    except IOError:
        print("Error: Workload file cant be opened")
        exit(1)

    # Reconstructs objects from given JSON files
    print("Reading Cluster Clocks file <" + ClusterClocksFileName + ">")
    ClusterClocks = json.loads(ClusterClocksFile.read())
    print("Done reading Cluster Clocks file")
    
    print("Building Topology")
    Topology = PlatformComposer.Platform().fromJSON(TopologyFile.read())
    print("Done building Topology")
    
    print("Building Workload")
    Workload = AppComposer.Workload().fromJSON(WorkloadFile.read())
    Workload.ParentPlatform = Topology
    print("Done building Workload")
    
    print("Building Allocation Map")
    AllocMap = json.loads(AllocMapFile.read())
    ThreadRefAllocMap = [[] for PE in range(Topology.AmountOfPEs)]  # Contains lists of references to Thread objects, indexed by a PEPos value
    AllocDict = dict()  # Contains PEPos values, indexed by thread names, as defined in Allocation Map
    
    # Checks if given Allocation Map is coherent with Topology
    if len(AllocMap) < Topology.AmountOfPEs:
        print("Error: Allocation Map size less than expected. <" + str(len(AllocMap)) + "> < <" + str(Topology.AmountOfPEs) + ">")
        exit(1)
    if len(AllocMap) > Topology.AmountOfPEs:
        print("Warning: Allocation Map size greater than expected <" + str(len(AllocMap)) + ">, truncating it to <" + str(Topology.AmountOfPEs) + ">")
    
    for PEPos, AllocMapItem in enumerate(AllocationMap[0:Topology.AmountOfPEs]):
        
        # Single Thread allocated to this PE
        if isinstance(AllocMapItem, str):
        
            # Get Thread object from thread name in Allocation Map
            ThreadInWorkload = self.Workload.getThread(ThreadName = AllocMapItem)
            
            # Checks if Thread, as defined in Allocation Map, exists in Workload
            if ThreadInWorkload is None:
                print("Error: Thread <" + str(AllocMapItem) + "> doesn't exist in given Workload")
                exit(1)
        
            # Checks if Thread has already been allocated
            if AllocMapItem in AllocDict.keys():
                print("Error: Thread <" + str(AllocMapItem) + "> has already been allocated at PE <" + str(AllocDict[AllocMapItem]) + ">")
                exit(1)
        
            # Add Thread to ThreadRefAllocMap
            ThreadRefAllocMap[PEPos].append(ThreadInWorkload)
            AllocDict[AllocMapItem] = PEPos
            
        # Multiple Threads allocated to this PE    
        elif isinstance(AllocMapItem, list):
            
            ThreadSet = [self.Workload.getThread(ThreadName = ThreadName) for ThreadName in AllocMapItem]
            
            #ThreadInWorkload.PEPos = PEPos
            for ThreadInSet in ThreadSet:
            
                # Get Thread object from thread name in Allocation Map
                ThreadName = ThreadInWorkload.ThreadName
                ThreadInWorkload = self.Workload.getThread(ThreadName = ThreadName)
                
                # Checks if Thread, as defined in Allocation Map, exists in Workload
                if ThreadInWorkload is None:
                    print("Error: Thread <" + str(ThreadName) + "> doesn't exist in given Workload")
                    exit(1)
        
                # Checks if Thread has already been allocated
                if ThreadName in AllocDict.keys():
                    print("Error: Thread <" + str(ThreadName) + "> has already been allocated at PE <" + str(AllocDict[ThreadName]) + ">")
                    exit(1)
            
                # Add Thread to ThreadRefAllocMap
                ThreadRefAllocMap[PEPos].append(ThreadInWorkload)
                AllocDict[ThreadName] = PEPos
                
                # TODO: Check if allocated Threads allocated to a same PE communicate between themselves, and if so, dont generate Injectors for those Flows
        
        elif AllocMapItem is None:

            print("Warning: PEPos <" + str(PEPos) + "> has no Thread allocated")
            
        else:

            print("Error: <AllocMapItem>'s type is not a string, list or None")
            exit(1)
    
    # Check if any Thread was left unallocated
    for App in Workload.Applications:
        for Thread in App.Threads:
            if AllocDict.get(Thread.ThreadName) is None:
                print("Error: Thread <" + Thread.ParentApplication.AppName + "." + Thread.ThreadName + "> was not allocated, aborting flowgen")
                exit(1)
    
    print("Done building Allocation Map\n")
    
    # Generates PE JSON config files at "flow/PE */PE *.json"
    for PEPos, PE in enumerate(Topology.PEs):
        with open(ProjectDir + "/flow/PE " + str(PEPos) + "/PE " + str(PEPos) + ".json", 'w') as PEFile:
            print("Generating config file for PE <" + str(PEPos) + ">")
            PE.updateWorkloadInfo(ThreadSet = ThreadRefAllocMap[PEPos])
            PEFile.write(PE.toJSON())
    
    # Generates Injector JSON config files at "flow/PE */Thread */Flow *.json"
    for PEPos, ThreadSet in enumerate(ThreadRefAllocMap):
        for ThreadNum, ThreadInSet in enumerate(ThreadSet):
            for FlowNum, OutgoingFlow in enumerate(ThreadInSet.OutgoingFlows):
                with open(ProjectDir + "/flow/PE " + str(PEPos) + "/Thread " + str(ThreadNum) + "/Flow " + str(FlowNum) + ".json", 'w') as InjectorFile:
                    print("Generating config file for Flow <" + str(OutgoingFlow) + ">")
                    InjectorFile.write(Injector(Flow = OutgoingFlow, DataWidth = Topology.DataWidth).toJSON())
                    
    # Generates Platform config file
    print("Generating Platform config file")
    shutil.copy(ProjectDir + "/src_json/Topology.json", ProjectDir + "/platform/PlatformConfig.json")
    
    # Generates Cluster Clocks config file
    print("Generating Cluster Clocks config file")
    with open(ProjectDir + "/platform/ClusterClocks.json", "w") as ClusterClocksFile:
    
        if len(ClusterClocks) < Topology.BaseNoCDimensions[0]*Topology.BaseNoCDimensions[1]:
            print("Error: ClusterClocks size less than expected. <" + str(len(ClusterClocks)) + "> < <" + str(Topology.BaseNoCDimensions[0]*Topology.BaseNoCDimensions[1]) + ">")
            exit(1)
        if len(ClusterClocks) > Topology.BaseNoCDimensions[0]*Topology.BaseNoCDimensions[1]:
            print("Warning: ClusterClocks size greater than expected, truncating it to <" + str(Topology.BaseNoCDimensions[0]*Topology.BaseNoCDimensions[1]) + ">")
        
        if isinstance(ClusterClocks, dict) and "ClusterClockPeriods" in ClusterClocks.keys():
            ClusterClocks = ClusterClocks["ClusterClockPeriods"][0:Topology.BaseNoCDimensions[0]*Topology.BaseNoCDimensions[1]]

        elif isinstance(ClusterClocks, dict) and "ClusterClockFrequencies" in ClusterClocks.keys():
            ClusterClocks = [float(1000/ClusterClocks["ClusterClockPeriods"][Cluster]) for Cluster in ClusterClocks["ClusterClockPeriods"][0:Topology.BaseNoCDimensions[0]*Topology.BaseNoCDimensions[1]]]  # MHz -> ns

        else:  # Assumes values are periods (in nanoseconds)
            self.ClusterClocks = ClusterClocks[0:self.BaseNoCDimensions[0]*self.BaseNoCDimensions[1]]
            
        ClusterClocksFile.write(json.dumps(ClusterClocks))
    
    with open(os.getenv("HIBRIDA_CONFIG_FILE"), "w") as ConfigFile:
        ConfigDict["MostRecentProject"] = args.ProjectName
        ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
    
    AllocMapFile.close()
    ClusterClocksFile.close()
    TopologyFile.close()
    WorkloadFile.close()

    print("flowgen executed successfully!")
