#!/usr/bin/python

# Arg 1 = Install name
# Arg 2 = Install path
# Arg 3 = Create executable flag

# TODO: PIP required libraries

import argparse

parser = argparse.ArgumentParser()

# Sets install name arg
parser.add_argument("-InstallName", help = "Name of command to be called from shell (<InstallName> flowgen , <InstallName> compile, ...). If not given, \"hibrida\" is used as default", type = str, default = "hibrida")

# Sets install path arg
import os
parser.add_argument("-InstallPath", help = "Path to framework source files. If not given, this scripts parent directory is used as default", type = str, default = os.path.abspath(".."))

# Sets default project directory
import platform
defaultProjDir = ""
if platform.system() == "Linux":
    #defaultProjDir = os.getenv("HOME") + "/Desktop/HibridaProjects"
    defaultProjDir = os.path.join(os.getenv("HOME"), "Desktop", "HibridaProjects")
elif platform.system() == "Windows":
    #defaultProjDir = os.getenv("userprofile") + "/Desktop/HibridaProjects"
    defaultProjDir = os.path.join(os.getenv("userprofile"), "Desktop", "HibridaProjects")
    
else:
    print("Error: OS <" + platform.system() + "> in not supported")
    exit(1)
    
parser.add_argument("-alo", "--AllocationMapsPath", help = "Default directory where Allocation Maps JSON files are stored. If not given, <InstallPath>/data/flowgen/allocationMaps will be used as default", type = str)
parser.add_argument("-app", "--ApplicationsPath", help = "Default directory where Application JSON files are stored. If not given, <InstallPath>/data/flowgen/applications will be used as default", type = str)
parser.add_argument("-clo", "--ClusterClocksPath", help = "Default directory where Cluster Clocks JSON files are stored. If not given, <InstallPath>/data/flowgen/clusterClocks will be used as default", type = str)
parser.add_argument("-top", "--TopologiesPath", help = "Default directory where Topology JSON files are stored. If not given, <InstallPath>/data/flowgen/topologies will be used as default", type = str)
parser.add_argument("-wor", "--WorkloadsPath", help = "Default directory where Workload JSON files are stored. If not given, <InstallPath>/data/flowgen/workloads will be used as default", type = str)

parser.add_argument("-DefaultProjDir", help = "Directory where projects will be created at as default. If not given, $HOME will be used as default", type = str, default = defaultProjDir)

args = parser.parse_args()

# Verify if .source file already exists, and if so, ask user if it should be replaced
if os.path.exists("../data/" + args.InstallName + ".source"):

    while True:
            
        print("Warning: .source file <" + os.path.abspath("../data/" + args.InstallName + ".source") + "> already exists. Do you wish to proceed (Y/N)?")
        #ipt = raw_input()
        ipt = input()
        
        if ipt == "Y" or ipt == "y":
            break
            
        elif ipt == "N" or ipt == "n":
            exit(0)

# Creates linux src file
with open("../data/" + args.InstallName + ".source", "w") as SourceFile:
    
    # Main paths
    SourceFile.write("export HIBRIDA_NAME=" + args.InstallName + "\n")
    SourceFile.write("export HIBRIDA_PATH=" + os.path.abspath(args.InstallPath) + "\n")
    SourceFile.write("export PATH=$PATH:$HIBRIDA_PATH/scripts\n")
    SourceFile.write("alias " + args.InstallName + "=\"python3 " + args.InstallPath + "/scripts/mainScript.py\"\n")
    SourceFile.write("export HIBRIDA_CONFIG_FILE=$HIBRIDA_PATH/data/config.json\n")
    #SourceFile.write("export HIBRIDA_DEFAULT_DIRECTORY=" + args.DefaultProjDir + "\n")
    
    # Hardware paths
    #SourceFile.write("export HIBRIDA_HARDWARE_PATH=$HIBRIDA_PATH/src/hardware\n")
    
    # Software paths
    #SourceFile.write("export HIBRIDA_SOFTWARE_PATH=$HIBRIDA_PATH/src/software\n")
    #SourceFile.write("export HIBRIDA_APPCOMPOSER_PATH=$HIBRIDA_SOFTWARE_PATH/AppComposer\n")
    #SourceFile.write("export HIBRIDA_PLATFORMCOMPOSER_PATH=$HIBRIDA_SOFTWARE_PATH/PlatformComposer\n")
    #SourceFile.write("export PYTHONPATH=$PYTHONPATH:$HIBRIDA_APPCOMPOSER_PATH\n")
    SourceFile.write("export PYTHONPATH=$PYTHONPATH:$HIBRIDA_PATH/src/software/AppComposer\n")
    #SourceFile.write("export PYTHONPATH=$PYTHONPATH:$HIBRIDA_PLATFORMCOMPOSER_PATH\n")
    SourceFile.write("export PYTHONPATH=$PYTHONPATH:$HIBRIDA_PATH/src/software/PlatformComposer\n")
    
    # Flowgen paths
    #SourceFile.write("export FLOWGEN_TOPOLOGIES_PATH=" + args.TopologiesPath + "\n")
    #SourceFile.write("export FLOWGEN_APPLICATIONS_PATH=" + args.ApplicationsPath + "\n")
    #SourceFile.write("export FLOWGEN_WORKLOADS_PATH=" + args.WorkloadsPath + "\n")
    #SourceFile.write("export FLOWGEN_ALLOCATIONMAPS_PATH=" + args.AllocationMapsPath + "\n")
    #SourceFile.write("export FLOWGEN_CLUSTERCLOCKS_PATH=" + args.ClusterClocksPath + "\n")

print("Created .source file at " + os.path.abspath("../data/" + args.InstallName + ".source"))
    
# Verify if .bat file already exists, and if so, ask user if it should be replaced
if os.path.exists("../data/" + args.InstallName + ".bat"):

    while True:
            
        print("Warning: .bat file <" + os.path.abspath("../data/" + args.InstallName + ".bat") + "> already exists. Do you wish to proceed (Y/N)?")
        #ipt = raw_input()
        ipt = input()
        
        if ipt == "Y" or ipt == "y":
            break
            
        elif ipt == "N" or ipt == "n":
            exit(0)
        
# Creates windows src file
with open("../data/" + args.InstallName + ".bat", "w") as SourceFile:
    
    # Main paths
    SourceFile.write("set HIBRIDA_NAME=" + args.InstallName + "\n")
    SourceFile.write("set HIBRIDA_PATH=" + os.path.abspath(args.InstallPath) + "\n")
    SourceFile.write("set PATH=%PATH%;%HIBRIDA_PATH%/scripts\n")
    SourceFile.write("doskey " + args.InstallName + "=(python " + args.InstallPath + "\scripts\mainScript.py $*)\n")
    SourceFile.write("set HIBRIDA_CONFIG_FILE=%HIBRIDA_PATH%/data/config.json\n")
    #SourceFile.write("set HIBRIDA_DEFAULT_DIRECTORY=" + args.DefaultProjDir + "\n")
    
    # Hardware paths
    #SourceFile.write("set HIBRIDA_HARDWARE_PATH=%HIBRIDA_PATH%/src/hardware\n")
    
    # Software paths
    #SourceFile.write("set HIBRIDA_SOFTWARE_PATH=%HIBRIDA_PATH%/src/software\n")
    #SourceFile.write("set HIBRIDA_APPCOMPOSER_PATH=%HIBRIDA_SOFTWARE_PATH%/AppComposer\n")
    #SourceFile.write("set HIBRIDA_PLATFORMCOMPOSER_PATH=%HIBRIDA_SOFTWARE_PATH%/PlatformComposer\n")
    #SourceFile.write("set PYTHONPATH=%PYTHONPATH%;%HIBRIDA_APPCOMPOSER_PATH%\n")
    SourceFile.write("set PYTHONPATH=%PYTHONPATH%;%HIBRIDA_PATH%/src/software/AppComposer\n")
    #SourceFile.write("set PYTHONPATH=%PYTHONPATH%;%HIBRIDA_PLATFORMCOMPOSER_PATH%\n")
    SourceFile.write("set PYTHONPATH=%PYTHONPATH%;%HIBRIDA_PATH%/src/software/PlatformComposer\n")
    
    # Flowgen paths
    #SourceFile.write("set FLOWGEN_TOPOLOGIES_PATH=" + args.TopologiesPath + "\n")
    #SourceFile.write("set FLOWGEN_APPLICATIONS_PATH=" + args.ApplicationsPath + "\n")
    #SourceFile.write("set FLOWGEN_WORKLOADS_PATH=" + args.WorkloadsPath + "\n")
    #SourceFile.write("set FLOWGEN_ALLOCATIONMAPS_PATH=" + args.AllocationMapsPath + "\n")
    #SourceFile.write("set FLOWGEN_CLUSTERCLOCKS_PATH=" + args.ClusterClocksPath + "\n")

print("Created .source file at " + os.path.abspath("../data/" + args.InstallName + ".source"))

# Creates config dict
dataDict = dict()

dataDict["AllocationMapsPaths"] = [args.AllocationMapsPath] if args.AllocationMapsPath is not None else [os.path.join(args.InstallPath, "data", "flowgen", "allocationMaps")]
dataDict["ApplicationsPaths"] = [args.ApplicationsPath] if args.ApplicationsPath is not None else [os.path.join(args.InstallPath, "data", "flowgen", "applications")]
dataDict["ClusterClocksPaths"] = [args.ClusterClocksPath] if args.ClusterClocksPath is not None else [os.path.join(args.InstallPath, "data", "flowgen", "clusterClocks")]
dataDict["TopologiesPaths"] = [args.TopologiesPath] if args.TopologiesPath is not None else [os.path.join(args.InstallPath, "data", "flowgen", "topologies")]
dataDict["WorkloadsPaths"] = [args.WorkloadsPath] if args.WorkloadsPath is not None else [os.path.join(args.InstallPath, "data", "flowgen", "workloads")]

dataDict["DefaultProjDir"] = args.DefaultProjDir
dataDict["HibridaConfigFile"] = args.InstallPath + "/data/config.json"
dataDict["HibridaName"] = args.InstallName
dataDict["HibridaPath"] = args.InstallPath

dataDict["Projects"] = dict()

# Verify if config file already exists, and if so, ask user if it should be replaced
if os.path.exists("../data/config.json"):

    while True:
            
        print("Warning: Config file <" + os.path.abspath("../data/config.json") + "> already exists. Do you wish to proceed (Y/N)?")
        #ipt = raw_input()
        ipt = input()
        
        if ipt == "Y" or ipt == "y":
            break
            
        elif ipt == "N" or ipt == "n":
            exit(0)
        
# Writes config dict to json file
with open("../data/config.json", "w") as ConfigFile:
    import json
    ConfigFile.write(json.dumps(dataDict, sort_keys = False, indent = 4))
    
# Verify if project list already exists, and if so, ask user if it should be replaced
if os.path.exists("../data/projectIndex.json"):
    
    while True:
            
        print("Warning: Config file <" + os.path.abspath("../data/projectIndex.json") + "> already exists. Do you wish to proceed (Y/N)?")
        #ipt = raw_input()
        ipt = input()
        
        if ipt == "Y" or ipt == "y":
            break
            
        elif ipt == "N" or ipt == "n":
            exit(0)
            
# Write empty dict as JSON to projectIndex
with open("../data/projectIndex.json", "w") as ConfigFile:
    import json
    ConfigFile.write(json.dumps(dict(), sort_keys = False, indent = 4))
            
print("Created config file at " + os.path.abspath("../data/config.json"))

print("Setup script ran successfully!")
