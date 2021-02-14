
def flowgen(args):

    import json
    import os
    import sys
    
    import PlatformComposer
    import AppComposer

    # Defines FileNotFoundError exception for Python 2 compatibility
    # try:
        # FileNotFoundError
    # except NameError:
        # FileNotFoundError = IOError
        # pass
    # except FileNotFoundError:
        # pass
        
    # Gets framework configs
    ConfigFile = open(os.getenv("HIBRIDA_CONFIG_FILE"), "r")
    ConfigDict = json.loads(ConfigFile.read())
    ProjectDir = ConfigDict["Projects"][args.ProjectName]["ProjectDir"]

    # Opens Allocation Map JSON file
    AllocMapFileName = ConfigDict["Projects"][args.ProjectName]["AllocationMapFile"]
        
    if AllocMapFileName is None:
        print("Error: Allocation Map file has not been set for project <" + args.ProjectName + ">. Aborting flowgen.")
        print("Please use the setConfig command with -a option to set an Allocation Map file")
        exit(1)
        
    try:
        AllocMapFile = open(AllocMapFileName, "r")
    except FileNotFoundError:
        print("Error: Allocation Map file <" + AllocMapFileName + "> not found")
        exit(1)
    except IOError:
        print("Error: Allocation Map file <" + AllocMapFileName + "> cant be opened")
        exit(1)
        
    # Opens Cluster Clocks JSON file
    ClusterClocksFileName = ConfigDict["Projects"][args.ProjectName]["ClusterClocksFile"]
        
    if ClusterClocksFileName is None:
        print("Error: Cluster Clocks file has not been set for project <" + args.ProjectName + ">. Aborting flowgen.")
        print("Please use the setConfig command with -c option to set a Cluster Clocks file")
        exit(1)
        
    try:
        ClusterClocksFile = open(ClusterClocksFileName, "r")
    except FileNotFoundError:
        print("Error: Cluster Clocks file <" + ClusterClocksFileName + "> not found")
        exit(1)
    except IOError:
        print("Error: Cluster Clocks file <" + ClusterClocksFileName + "> cant be opened")
        exit(1)
        
    # Opens Topology JSON file
    TopologyFileName = ConfigDict["Projects"][args.ProjectName]["TopologyFile"]
        
    if TopologyFileName is None:
        print("Error: Topology file has not been set for project <" + args.ProjectName + ">. Aborting flowgen.")
        print("Please use the setConfig command with -t option to set a Topology file")
        exit(1)
        
    try:
        TopologyFile = open(TopologyFileName, "r")
    except FileNotFoundError:
        print("Error: Topology file <" + TopologyFileName + "> not found")
        exit(1)
    except IOError:
        print("Error: Topology file <" + TopologyFileName + "> cant be opened")
        exit(1)
    
    # Opens Workload JSON file
    WorkloadFileName = ConfigDict["Projects"][args.ProjectName]["WorkloadFile"]
        
    if WorkloadFileName is None:
        print("Error: Workload file has not been set for project <" + args.ProjectName + ">. Aborting flowgen.")
        print("Please use the setConfig command with -w option to set a Workload file")
        exit(1)
        
    try:
        WorkloadFile = open(WorkloadFileName, "r")
    except FileNotFoundError:
        print("Error: Workload file <" + WorkloadFile + "> not found")
        exit(1)
    except IOError:
        print("Error: Workload file <" + WorkloadFile + "> cant be opened")
        exit(1)

    # Reconstructs objects from given JSON files
    print("Reading Allocation Map file <" + AllocMapFileName + ">")
    AllocMap = json.loads(AllocMapFile.read())
    print("Done reading Allocation Map file")
    
    print("Reading Cluster Clocks file <" + ClusterClocksFileName + ">")
    ClusterClocks = json.loads(ClusterClocksFile.read())
    print("Done reading Cluster Clocks file")
    
    print("Building Platform object from <" + TopologyFileName + ">")
    Platform = PlatformComposer.Platform(BaseNoCDimensions = (2,2), ReferenceClock = 10)  # Dummy constructor arguments, will be replaced by those in JSON file
    Platform.fromJSON(TopologyFile.read())
    print("Done building Platform object")
    
    print("Building Workload object from <" + WorkloadFileName + ">")
    Workload = AppComposer.Workload()
    Workload.fromJSON(WorkloadFile.read())
    print("Done building Workload object")
    
    # Generates PE and Injector JSON config files at given project dir
    print("Implementing Workload to Platform")
    Platform.setWorkload(Workload)
    print("Done implementing Workload to Platform")
    
    print("Implementing AllocationMap to Platform")
    print(AllocMap)
    Platform.setAllocationMap(AllocMap)
    print("Done implementing AllocationMap to Platform")

    print("Implementing ClusterClocks to Platform")
    Platform.setClusterClocks(ClusterClocks)
    print("Done implementing ClusterClocks to Platform")

    print("Generating Platform JSON file")
    Platform.generateJSON(ConfigDict["Projects"][args.ProjectName]["ProjectDir"])
    print("Done generating Platform JSON file")
    print("JSON config files created at <" + os.path.join(ProjectDir, "flow") + ">")

    # Generate blank log text files for every PE
    # for i in range(Platform.AmountOfPEs):
        # logFile = open(args.ProjectDir + "/log/InLog" + str(i) + ".txt", "w")
        # logFile.close()
        # logFile = open(args.ProjectDir + "/log/OutLog" + str(i) + ".txt", "w")
        # logFile.close()

    # Copies .json files to project dir
    from shutil import copy
    SRCJSONBasePath = os.path.join(ProjectDir, "src_json")
    copy(AllocMapFileName, os.path.join(SRCJSONBasePath, "AllocationMap.json"))
    copy(ClusterClocksFileName, os.path.join(SRCJSONBasePath, "ClusterClocks.json"))
    copy(TopologyFileName, os.path.join(SRCJSONBasePath, "Topology.json"))
    copy(WorkloadFileName, os.path.join(SRCJSONBasePath, "Workload.json"))
    
    # Generate log containing project information
    # ProjectInfo = open(args.ProjectDir + "/" + "ProjectInfo.txt", 'w')
    # ProjectInfo.write("Topology: " + TopologyFileName + "\n")
    # ProjectInfo.write("\tAmount of PEs: " + str(Setup.AmountOfPEs) + "\n")
    # ProjectInfo.write("\tAmount of PEs in base NoC: " + str((Setup.BaseNoCDimensions[0] * Setup.BaseNoCDimensions[1]) - Setup.AmountOfWrappers) + "\n")
    # ProjectInfo.write("\tAmount of Wrappers: " + str(Setup.AmountOfWrappers) + "\n")

    # ProjectInfo.write("\tAmount of Buses: " + str(Setup.AmountOfBuses) + "\n")
    # AmountOfPEsInBuses = 0
    # for Bus in Setup.Buses:
    #     AmountOfPEsInBuses += len(Bus.PEs)
    # ProjectInfo.write("\tAmount of PEs in each Bus: " + str(Setup.AmountOfPEsInBuses) + "\n")

    # ProjectInfo.write("\tAmount of Crossbars: " + str(Setup.AmountOfCrossbars) + "\n")
    # AmountOfPEsInCrossbars = 0
    # for Crossbar in Setup.Crossbars:
    #     AmountOfPEsInCrossbars += len(Crossbar.PEs)
    # ProjectInfo.write("\tAmount of PEs in each Crossbar: " + str(Setup.AmountOfPEsInCrossbars) + "\n")

    # ProjectInfo.write("Application: " + "\n")
    # ProjectInfo.write("\tNumber of Applications: " + str(len(Applications)) + "\n")

    # Threads = []
    # for App in Applications:
    #     for Thread in App.Threads:
    #         Threads.append(Thread)
    # ProjectInfo.write("\tNumber of Threads: " + str(len(Threads)) + "\n")

    # Targets = []
    # for Thread in Threads:
    #     for Target in Thread.Targets:
    #         Targets.append(Target)
    # ProjectInfo.write("\tAmount of Targets: " + str(len(Targets)) + "\n")

    # Bandwidth = []
    # for Thread in Threads:
    #     Bandwidth.append(Thread.TotalBandwidth)
    # ProjectInfo.write("\tTotal required bandwidth: " + str(sum(Bandwidth)) + "\n")

    #ProjectInfo.write("\tAverage required bandwidth (per thread): " + str(statistics.mean(Bandwidth)) + "\n")
    #ProjectInfo.write("\tStd deviation of required bandwidth (per thread): " + str(statistics.pstdev(Bandwidth)) + "\n")

    # TODO: Classify application as concentrated or distributed (function of std dev) and high demand or low demand

    # Classify application as concentrated or distributed
    # BandwidthNormalized = preprocessing.normalize([Bandwidth])
    # if statistics.pstdev(BandwidthNormalized) > 0.35:
    #     ProjectInfo.write("\n\tApplication is concentrated")
    # else:
    #     ProjectInfo.write("\n\tApplication is distributed")
    #
    # # Classify as high demand or low demand
    # if statistics.mean(Bandwidth) > 100:  # Bandwidth is expressed in Mbps
    #     ProjectInfo.write("\tApplication is high demand")
    # else:
    #     ProjectInfo.write("\tApplication is low demand")

    #ProjectInfo.close()
    
    ConfigFile.close()
    AllocMapFile.close()
    ClusterClocksFile.close()
    TopologyFile.close()
    WorkloadFile.close()

    print("flowgen ran successfully!")
