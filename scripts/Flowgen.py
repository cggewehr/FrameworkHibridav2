
def flowgen(args):

    import sys
    import os
    import json as JSON
    import PlatformComposer
    import AppComposer

    # Defines FileNotFoundError exception for Python 2 compatibility
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = IOError
        pass
    except FileNotFoundError:
        pass
        
    # TODO: Checks if dir args.ProjectDir exists

    # Sets arguments
    # $0 = Name of setup JSON file
    try:
        TopologyFileName = str(args.TopologyFile)
    except KeyError or IndexError:
        print("Error: Flowgen argument <TopologyFile> not given")
        exit(1)
    
    # $1 = Name of application JSON file
    try:
        WorkloadFileName = str(args.WorkloadFile)
    except KeyError or IndexError:
        print("Error: Flowgen argument <WorkloadFile> not given")
        exit(1)
        
    # $2 = Name of allocation map JSON file
    try:
        AllocMapFileName = str(args.AllocMapFile)
    except KeyError or IndexError:
        print("Error: Flowgen argument <AllocMapFile> not given")
        exit(1)
        
    # $3 = Name of cluster clock JSON file
    try:
        ClusterClocksFileName = str(args.ClusterClocksFile)
    except KeyError or IndexError:
        print("Error: Flowgen argument <ClusterClocksFile> not given")
        exit(1)
        

    # Adds Topologies info path
    try:
        TopologyPath = str(os.getenv("FLOWGEN_TOPOLOGIES_PATH"))
    except KeyError:
        print("Warning: Environment variable \"FLOWGEN_TOPOLOGIES\" not found. \"FLOWGEN_SOURCES\" must be the directory which contains network topology information in JSON format")

    # Adds Applications info path
    try:
        WorkloadPath = str(os.getenv("FLOWGEN_WORKLOADS_PATH"))
    except KeyError:
        print("Warning: Environment variable \"FLOWGEN_WORKLOADS\" not found. \"FLOWGEN_WORKLOADS\" must be the directory which contains application descriptions in JSON format")

    # Adds Allocation Maps info path
    try:
        AllocMapPath = str(os.getenv("FLOWGEN_ALLOCATIONMAPS_PATH"))
    except KeyError:
        print("Warning: Environment variable \"FLOWGEN_ALLOCATIONMAPS\" not found. \"FLOWGEN_ALLOCATIONMAPS\" must be the directory which contains application mapping information in JSON format")
        
    # Adds Clocks info path
    try:
        ClusterClocksPath = str(os.getenv("FLOWGEN_CLUSTERCLOCKS_PATH"))
    except KeyError:
        print("Warning: Environment variable \"FLOWGEN_CLUSTERCLOCKS\" not found. \"FLOWGEN_CLUSTERCLOCKS\" must be the directory which contains cluster clock frequency information in JSON format")


    # Opens Topology JSON file
    try:
        TopologyFile = open(TopologyPath + "/" + TopologyFileName + ".json")
    except FileNotFoundError:
        print("Error: Given Topology file \"" + str(TopologyFileName) + "\" not found at \"" + TopologyPath + "\". (.json extension is automatically added to given file name)")
        exit(1)
    
    # Opens Workload JSON file
    try:
        WorkloadFile = open(WorkloadPath + "/" + WorkloadFileName + ".json")
    except FileNotFoundError:
        print("Error: Given Workload file \"" + str(WorkloadFileName) + "\" not found at \"" + WorkloadPath + "\". (.json extension is automatically added to given file name)")
        exit(1)

    # Opens AllocMap JSON file
    try:
        AllocMapFile = open(AllocMapPath + "/" + AllocMapFileName + ".json")
    except FileNotFoundError:
        print("Error: Given Allocation Map file \"" + str(AllocMapFileName) + "\" not found at \"" + AllocMapPath + "\". (.json extension is automatically added to given file name)")
        exit(1)
        
    # Opens Topology JSON file
    try:
        ClusterClocksFile = open(ClusterClocksPath + "/" + ClusterClocksFileName + ".json")
    except FileNotFoundError:
        print("Error: Given Allocation Map file \"" + str(ClusterClocksFileName) + "\" not found at \"" + ClusterClocksPath + "\". (.json extension is automatically added to given file name)")
        exit(1)

    # Reconstructs objects from given JSON files
    Platform = PlatformComposer.Platform(BaseNoCDimensions = (2,2), ReferenceClock = 10)  # Dummy constructor arguments, will be replaced by those in JSON file
    Platform.fromJSON(TopologyFile.read())
    
    Workload = AppComposer.Workload()
    Workload.fromJSON(WorkloadFile.read())
    
    AllocMap = JSON.loads(AllocMapFile.read())
    
    ClusterClocks = JSON.loads(ClusterClocksFile.read())
    
    #
    Platform.setWorkload(Workload)
    Platform.setAllocationMap(AllocMap)
    Platform.setClusterClocks(ClusterClocks)
    
    # Generates PE and Injector JSON config files at given project dir
    Platform.generateJSON(args.ProjectDir + "/flow/")

    # Generate blank log text files for every PE
    for i in range(Setup.AmountOfPEs):
        logFile = open(ProjectDir + "/log/InLog" + str(i) + ".txt", "w")
        logFile.close()
        logFile = open(ProjectDir + "/log/OutLog" + str(i) + ".txt", "w")
        logFile.close()

    # Copies .json files to project dir
    from shutil import copy
    copy(args.TopologyFile, args.ProjectDir + "/Topology.json")
    copy(args.WorkloadFile, args.ProjectDir + "/Workload.json")
    copy(args.AllocMapFile, args.ProjectDir + "/AllocMap.json")
    copy(args.ClusterClocksFile, args.ProjectDir + "/AllocMap.json")
        
    # Generate log containing project information
    ProjectInfo = open(ProjectDir + "/" + "ProjectInfo.txt", 'w')
    ProjectInfo.write("Setup: " + SetupScript + "\n")
    ProjectInfo.write("\tAmount of PEs: " + str(Setup.AmountOfPEs) + "\n")
    ProjectInfo.write("\tAmount of PEs in base NoC: " + str((Setup.BaseNoCDimensions[0] * Setup.BaseNoCDimensions[1]) - Setup.AmountOfWrappers) + "\n")
    ProjectInfo.write("\tAmount of Wrappers: " + str(Setup.AmountOfWrappers) + "\n")

    ProjectInfo.write("\tAmount of Buses: " + str(Setup.AmountOfBuses) + "\n")
    AmountOfPEsInBuses = 0
    for Bus in Setup.Buses:
        AmountOfPEsInBuses += len(Bus.PEs)
    ProjectInfo.write("\tAmount of PEs in each Bus: " + str(Setup.AmountOfPEsInBuses) + "\n")

    ProjectInfo.write("\tAmount of Crossbars: " + str(Setup.AmountOfCrossbars) + "\n")
    AmountOfPEsInCrossbars = 0
    for Crossbar in Setup.Crossbars:
        AmountOfPEsInCrossbars += len(Crossbar.PEs)
    ProjectInfo.write("\tAmount of PEs in each Crossbar: " + str(Setup.AmountOfPEsInCrossbars) + "\n")

    ProjectInfo.write("Application: " + "\n")
    ProjectInfo.write("\tNumber of Applications: " + str(len(Applications)) + "\n")

    Threads = []
    for App in Applications:
        for Thread in App.Threads:
            Threads.append(Thread)
    ProjectInfo.write("\tNumber of Threads: " + str(len(Threads)) + "\n")

    Targets = []
    for Thread in Threads:
        for Target in Thread.Targets:
            Targets.append(Target)
    ProjectInfo.write("\tAmount of Targets: " + str(len(Targets)) + "\n")

    Bandwidth = []
    for Thread in Threads:
        Bandwidth.append(Thread.TotalBandwidth)
    ProjectInfo.write("\tTotal required bandwidth: " + str(sum(Bandwidth)) + "\n")

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
    
    
    # TODO: Close JSON files
    TopologyFile.close()
    WorkloadFile.close()
    AllocMapFile.close()
    ClusterClocks.close()
    
    ProjectInfo.close()

    # Print final messages and exit successfully
    print("JSON config files created at " + ProjectDir + "/flow/")
    print("Project info file created at " + ProjectDir)
    print("Exiting successfully\n")
    exit(0)
