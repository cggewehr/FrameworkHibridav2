import os
import json

def setConfig(args):

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
    
    # Set project's Allocation Map file
    if args.AllocationMapFile:
    
        # Verifies if an Allocation Map file has already been set for this project
        if os.path.isfile(ProjectDir + "/src_json/AllocationMap.json"):
        
            while True:
        
                print("Warning: Project <" + args.ProjectName + "> already has <" + os.path.abspath(ProjectDict["AllocationMapFile"]) + "> set as its Allocation Map file. Replace it? (Y/N)")
                ipt = input()
                
                if ipt == "Y" or ipt == "y":
                    break
                    
                elif ipt == "N" or ipt == "n":
                    exit(0)
            
        AllocationMapFile = ""
        AbsFlag = False
        FoundIndexes = []
        
        # Determines which file to use
        if os.path.isabs(args.AllocationMapFile):
        
            AllocationMapFile = args.AllocationMapFile
            AbsFlag = True
            FoundIndexes.append(0)
            
        else:
        
            # Loops through search path to file given file
            for PathIndex, AllocationMapPath in enumerate(ConfigDict["AllocationMapsPaths"]):
                
                TentativePath = os.path.join(AllocationMapPath, args.AllocationMapFile)
                
                if os.path.exists(TentativePath):
                    print("Found file <" + TentativePath + ">")
                    #AllocationMapFile = TentativePath
                    FoundIndexes.append(PathIndex)
                    
        # Resolves possible conflicts
        if len(FoundIndexes) == 0:
            print("Error: Given AllocationMapFile <" + args.AllocationMapFile + "> cant be found. Try using an absolute path instead or adding its base path to the AllocationMapPaths parameter through the AddSearchPath command.")
            exit(1)
            
        elif len(FoundIndexes) == 1:
            if not AbsFlag:
                AllocationMapFile = os.path.join(ConfigDict["AllocationMapsPaths"][FoundIndexes[0]], args.AllocationMapFile)
            
        else:
                
            while True:
    
                # Multiple matching files found
                print("Warning: Multiple valid files found. Please select which one to use: " + str(range(len(FoundIndexes))) + " or N to exit")
                
                for i, pathIndex in enumerate(FoundIndexes):
                    print("\t" + str(i) + ": " + ConfigDict["AllocationMapsPaths"][pathIndex])
                    
                #ipt = raw_input()
                ipt = input()
                
                if int(ipt) in range(FoundIndexes):
                    AllocationMapFile = os.path.join(ConfigDict["AllocationMapsPaths"][FoundIndexes[int(ipt)]], args.AllocationMapFile)
                    break
                    
                elif ipt == "N" or ipt == "n":
                    exit(0)
        
        # Checks if given file is a valid json file
        try:
            #JSONTestDict = json.loads(open(args.AllocationMapFile).read())
            json.loads(open(AllocationMapFile).read())
        except ValueError:
            print("Error: AllocationMapFile <" + os.path.abspath(AllocationMapFile) + "> does not contain valid JSON")
            exit(1)
        except FileNotFoundError:
            print("Error: AllocationMapFile <" + os.path.abspath(AllocationMapFile) + "> cant be found")  # FileNotFoundError exception only exists in Python 3
            exit(1)
        except IOError:
            print("Error: AllocationMapFile <" + os.path.abspath(AllocationMapFile) + "> cant be opened")
            exit(1)

        #ConfigDict["Projects"][args.ProjectName]["AllocationMapFile"] = AllocationMapFile
        copy(AllocationMapFile, os.path.join(ProjectDir, "src_json", "AllocationMap.json"))
        ProjectDict["AllocationMapFile"] = AllocationMapFile
        print("Project <" + args.ProjectName + "> Allocation Map File set as <" + os.path.abspath(AllocationMapFile) + ">")
    
    if args.ClusterClocksFile:
    
        # Verifies if a Cluster Clocks file has already been set for this project
        if os.path.isfile(ProjectDir + "/src_json/ClusterClocks.json"):
        
            while True:
        
                print("Warning: Project <" + args.ProjectName + "> already has <" + os.path.abspath(ProjectDict["ClusterClocksFile"]) + "> set as its Cluster Clocks file. Replace it? (Y/N)")
                ipt = input()
                
                if ipt == "Y" or ipt == "y":
                    break
                    
                elif ipt == "N" or ipt == "n":
                    exit(0)
                    
        ClusterClocksFile = ""
        AbsFlag = False
        FoundIndexes = []
        
        # Determines which file to use
        if os.path.isabs(args.ClusterClocksFile):
        
            ClusterClocksFile = args.ClusterClocksFile
            AbsFlag = True
            FoundIndexes.append(0)
            
        else:
        
            # Loops through search path to file given file
            for PathIndex, ClusterClocksPath in enumerate(ConfigDict["ClusterClocksPaths"]):
                
                TentativePath = os.path.join(ClusterClocksPath, args.ClusterClocksFile)
                
                if os.path.exists(TentativePath):
                    print("Found file <" + TentativePath + ">")
                    #ClusterClocksFile = TentativePath
                    FoundIndexes.append(PathIndex)
                    
        # Resolves possible conflicts
        if len(FoundIndexes) == 0:
            print("Error: Given ClusterClocksFile <" + args.ClusterClocksFile + "> cant be found. Try using an absolute path instead or adding its base path to the ClusterClocksPaths parameter through the AddSearchPath command.")
            exit(1)
            
        elif len(FoundIndexes) == 1:
            if not AbsFlag:
                ClusterClocksFile = os.path.join(ConfigDict["ClusterClocksPaths"][FoundIndexes[0]], args.ClusterClocksFile)
            
        else:
                
            while True:
    
                # Multiple matching files found
                print("Warning: Multiple valid files found. Please select which one to use: " + str(range(len(FoundIndexes))) + " or N to exit")
                
                for i, pathIndex in enumerate(FoundIndexes):
                    print("\t" + str(i) + ": " + ConfigDict["ClusterClocksPaths"][pathIndex])
                    
                ipt = input()
                
                if int(ipt) in range(FoundIndexes):
                    ClusterClocksFile = os.path.join(ConfigDict["ClusterClocksPaths"][FoundIndexes[int(ipt)]], args.ClusterClocksFile)
                    break
                    
                elif ipt == "N" or ipt == "n":
                    exit(0)
                    
        # Checks if given file is a valid json file
        try:
            json.loads(open(ClusterClocksFile).read())
        except ValueError:
            print("Error: Given ClusterClocksFile <" + args.ClusterClocksFile + "> does not contain valid JSON")
            exit(1)
        except FileNotFoundError:
            print("Error: Given ClusterClocksFile <" + args.ClusterClocksFile + "> cant be found")  # FileNotFoundError exception only exists in Python 3
            exit(1)
        except IOError:
            print("Error: Given ClusterClocksFile <" + args.ClusterClocksFile + "> cant be opened")
            exit(1)

        #ConfigDict["Projects"][args.ProjectName]["ClusterClocksFile"] = ClusterClocksFile
        copy(ClusterClocksFile, os.path.join(ProjectDir, "src_json", "AllocationMap.json"))
        ProjectDict["ClusterClocksFile"] = ClusterClocksFile
        print("Project <" + args.ProjectName + "> Cluster Clocks file set as <" + os.path.abspath(ClusterClocksFile) + ">")
    
    if args.TopologyFile:
    
        #if ConfigDict["Projects"][args.ProjectName]["TopologyFile"] is not None:
        if os.path.isfile(ProjectDir + "/src_json/Topology.json"):
        
            while True:
        
                print("Warning: Project <" + args.ProjectName + "> already has <" + os.path.abspath(ProjectDict["TopologyFile"]) + "> set as its Topology file. Replace it? (Y/N)")

                ipt = input()
                
                if ipt == "Y" or ipt == "y":
                    break
                    
                elif ipt == "N" or ipt == "n":
                    exit(0)
                    
        TopologyFile = ""
        AbsFlag = False
        FoundIndexes = []
        
        # Determines which file to use
        if os.path.isabs(args.TopologyFile):
        
            TopologyFile = args.TopologyFile
            AbsFlag = True
            FoundIndexes.append(0)
            
        else:
        
            # Loops through search path to file given file
            for PathIndex, ClusterClocksPath in enumerate(ConfigDict["TopologiesPaths"]):
                
                TentativePath = os.path.join(ClusterClocksPath, args.TopologyFile)
                
                if os.path.exists(TentativePath):
                    print("Found file <" + TentativePath + ">")
                    #TopologyFile = TentativePath
                    FoundIndexes.append(PathIndex)
                    
        # Resolves possible conflicts
        if len(FoundIndexes) == 0:
            print("Error: Given TopologyFile <" + args.TopologyFile + "> cant be found. Try using an absolute path instead or adding its base path to the TopologiesPaths parameter through the AddSearchPath command.")
            exit(1)
            
        elif len(FoundIndexes) == 1:
            if not AbsFlag:
                TopologyFile = os.path.join(ConfigDict["TopologiesPaths"][FoundIndexes[0]], args.TopologyFile)
            
        else:
                
            while True:
    
                # Multiple matching files found
                print("Warning: Multiple valid files found. Please select which one to use: " + str(range(len(FoundIndexes))) + " or N to exit")
                
                for i, pathIndex in enumerate(FoundIndexes):
                    print("\t" + str(i) + ": " + ConfigDict["TopologiesPaths"][pathIndex])
                    
                #ipt = raw_input()
                ipt = input()
                
                if int(ipt) in range(FoundIndexes):
                    TopologyFile = os.path.join(ConfigDict["TopologiesPaths"][FoundIndexes[int(ipt)]], args.TopologyFile)
                    break
                    
                elif ipt == "N" or ipt == "n":
                    exit(0)
                    
        # Checks if given file is a valid json file
        try:
            #JSONTestDict = json.loads(open(args.TopologyFile).read())
            json.loads(open(TopologyFile).read())
        except ValueError:
            print("Error: Given TopologyFile <" + TopologyFile + "> does not contain valid JSON")
            exit(1)
        except FileNotFoundError:
            print("Error: Given TopologyFile <" + TopologyFile + "> cant be found")  # FileNotFoundError exception only exists in Python 3
            exit(1)
        except IOError:
            print("Error: Given TopologyFile <" + TopologyFile + "> cant be opened")
            exit(1)
        
        #ConfigDict["Projects"][args.ProjectName]["TopologyFile"] = TopologyFile
        copy(TopologyFile, os.path.join(ProjectDir, "src_json", "Topology.json"))
        ProjectDict["TopologyFile"] = TopologyFile
        print("Project <" + args.ProjectName + "> Topology file set as <" + TopologyFile + ">")
            
    if args.WorkloadFile:
    
        #if ConfigDict["Projects"][args.ProjectName]["WorkloadFile"] is not None:
        if os.path.isfile(ProjectDir + "/src_json/Workload.json"):
        
            while True:
        
                print("Warning: Project <" + args.ProjectName + "> already has <" + os.path.abspath(ProjectDict["WorkloadFile"]) + "> set as its Workload file. Replace it? (Y/N)")

                ipt = input()
                
                if ipt == "Y" or ipt == "y":
                    break
                    
                elif ipt == "N" or ipt == "n":
                    exit(0)
                    
        WorkloadFile = ""
        AbsFlag = False
        FoundIndexes = []
        
        # Determines which file to use
        if os.path.isabs(args.WorkloadFile):
        
            WorkloadFile = args.WorkloadFile
            AbsFlag = True
            FoundIndexes.append(0)
            
        else:
        
            # Loops through search path to file given file
            for PathIndex, ClusterClocksPath in enumerate(ConfigDict["WorkloadsPaths"]):
                
                TentativePath = os.path.join(ClusterClocksPath, args.WorkloadFile)
                
                if os.path.exists(TentativePath):
                    print("Found file <" + TentativePath + ">")
                    #WorkloadFile = TentativePath
                    FoundIndexes.append(PathIndex)
                    
        # Resolves possible conflicts
        if len(FoundIndexes) == 0:
            print("Error: Given WorkloadFile <" + args.WorkloadFile + "> cant be found. Try using an absolute path instead or adding its base path to the WorkloadsPaths parameter through the AddSearchPath command.")
            exit(1)
            
        elif len(FoundIndexes) == 1:
            if not AbsFlag:
                WorkloadFile = os.path.join(ConfigDict["WorkloadsPaths"][FoundIndexes[0]], args.WorkloadFile)
            
        else:
                
            while True:
    
                # Multiple matching files found
                print("Warning: Multiple valid files found. Please select which one to use: " + str(range(len(FoundIndexes))) + " or N to exit")
                
                for i, pathIndex in enumerate(FoundIndexes):
                    print("\t" + str(i) + ": " + ConfigDict["WorkloadsPaths"][pathIndex])
                    
                #ipt = raw_input()
                ipt = input()
                
                if int(ipt) in range(FoundIndexes):
                    WorkloadFile = os.path.join(ConfigDict["WorkloadsPaths"][FoundIndexes[int(ipt)]], args.WorkloadFile)
                    break
                    
                elif ipt == "N" or ipt == "n":
                    exit(0)
                         
        # Checks if given file is a valid json file
        try:
            #JSONTestDict = json.loads(open(args.WorkloadFile).read())
            json.loads(open(WorkloadFile).read())
        except ValueError:
            print("Error: Given WorkloadFile <" + WorkloadFile + "> does not contain valid JSON")
            exit(1)
        except FileNotFoundError:
            print("Error: Given WorkloadFile <" + args.WorkloadFile + "> cant be found")  # FileNotFoundError exception only exists in Python 3
            exit(1)
        except IOError:
            print("Error: Given WorkloadFile <" + args.WorkloadFile + "> cant be opened")
            exit(1)

        #ConfigDict["Projects"][args.ProjectName]["WorkloadFile"] = WorkloadFile
        copy(WorkloadFile, os.path.join(ProjectDir, "src_json", "Workload.json"))
        ProjectDict["WorkloadFile"] = WorkloadFile
        print("Project <" + args.ProjectName + "> Workload file set as <" + WorkloadFile + ">")
            
    # Displays which AllocationMap/ClusterClocks/Topology/Workloads config files have been associated to current project
    if args.state:
    
        print("\nProject Name: " + str(ProjectDict["ProjectName"]))
        print("Project Directory: " + str(ProjectDict["ProjectDir"]))
        print("Allocation Map file: " + str(ProjectDict["AllocationMapFile"]))
        print("Cluster Clocks file: " + str(ProjectDict["ClusterClocksFile"]))
        print("Topology file: " + str(ProjectDict["TopologyFile"]))
        print("Workload file: " + str(ProjectDict["WorkloadFile"]) + "\n")
    
    if args.AllocationMapFile is not None or args.ClusterClocksFile is not None or args.TopologyFile is not None or args.WorkloadFile is not None:
    
        print("Writing modifications to config file")
        
        with open(ProjectDir + "/projectInfo.json", "w") as ProjectInfoFile:
            ProjectInfoFile.write(json.dumps(ProjectDict, sort_keys = False, indent = 4))
            
        with open(os.getenv("HIBRIDA_CONFIG_FILE"), "w") as ConfigFile:
            ConfigDict["MostRecentProject"] = args.ProjectName
            ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
        
    print("setConfig ran successfully!")
    
