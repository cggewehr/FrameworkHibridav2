import json
import os

def addSearchPath(args):

    # Gets framework configs
    ConfigFile = open(os.getenv("HIBRIDA_CONFIG_FILE"), "r")
    ConfigDict = json.loads(ConfigFile.read())
    
    if args.AllocationMapsPath:
        for NewPath in args.AllocationMapsPath:
            ConfigDict["AllocationMapsPaths"].append(NewPath)
            
    if args.ApplicationsPath:
        for NewPath in args.ApplicationsPath:
            ConfigDict["ApplicationsPaths"].append(NewPath)
            
    if args.ClusterClocksPath:
        for NewPath in args.ClusterClocksPath:
            ConfigDict["ClusterClocksPaths"].append(NewPath)
    
    if args.TopologiesPath:
        for NewPath in args.TopologiesPath:
            ConfigDict["TopologiesPaths"].append(NewPath)
    
    if args.WorkloadPath:
        for NewPath in args.WorkloadPath:
            ConfigDict["WorkloadPaths"].append(NewPath)
    
    # Write path changes to config file
    ConfigFile.close()
    with open(os.getenv("HIBRIDA_CONFIG_FILE"), "w") as ConfigFile:
        ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
        
    print("addSearchPath ran successfully!")
    