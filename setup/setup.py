#!/usr/bin/python

# Arg 1 = Install name
# Arg 2 = Install path
# Arg 3 = Create executable flag

# TODO: PIP required libraries

import argparse

parser = argparse.ArgumentParser()

# Sets install name arg
parser.add_argument("-InstallName", help = "Name of command to be called from shell (<InstallName> flowgen ...). If not given, \"hibrida\" is used as default", type = str, default = "hibrida")

# Sets install path arg
import os
parser.add_argument("-InstallPath", help = "Path to framework source files. If not given, this scripts parent directory is used as default", type = str, default = os.path.abspath(".."))

# Sets default project directory
import platform
defaultProjDir = ""
if platform.system() == "Linux":
    defaultProjDir = os.getenv("HOME") + "\HibridaProjects"
elif platform.system() == "Windows":
    defaultProjDir = os.getenv("userprofile") + "\Desktop\HibridaProjects"
else:
    print("Error: OS <" + platform.system() + "> in not supported")
    exit(1)
    
parser.add_argument("-DefaultProjDir", help = "Directory where projects will be created at as default. If not given, $HOME will be used as default", type = str, default = defaultProjDir)

parser.add_argument("-t", "-T", "--TopologiesPath", help = "Default directory where Topology JSON files are stored. If not given, <InstallPath>/flowgenData/Topologies will be used as default", type = str, default = "$HIBRIDA_PATH/flowgenData/Topologies")
parser.add_argument("-w", "-W", "--WorkloadsPath", help = "Default directory where Workload JSON files are stored. If not given, <InstallPath>/flowgenData/Workloads will be used as default", default = "$HIBRIDA_PATH/flowgenData/Workloads", type = str)
parser.add_argument("-a", "-A", "--AllocationMapsPath", help = "Default directory where Allocation Maps JSON files are stored. If not given, <InstallPath>/flowgenData/AllocationMaps will be used as default", default = "$HIBRIDA_PATH/flowgenData/AllocationMaps", type = str)
parser.add_argument("-c", "-C", "--ClusterClocksPath", help = "Default directory where Cluster Clocks JSON files are stored. If not given, <InstallPath>/flowgenData/ClusterClocks will be used as default", default = "$HIBRIDA_PATH/flowgenData/ClusterClocks", type = str)

args = parser.parse_args()

# Creates linux src file
with open(args.InstallName + ".source", "w") as SourceFile:
    
    # Main paths
    SourceFile.write("export $HIBRIDA_NAME=" + args.InstallName + "\n")
    SourceFile.write("export $HIBRIDA_PATH=" + args.InstallPath + "\n")
    SourceFile.write("export $PATH=$PATH:$HIBRIDA_PATH/scripts\n")
    SourceFile.write("alias " + args.InstallName + "=./" + args.InstallPath + "/scripts/mainScript\n")
    SourceFile.write("export HIBRIDA_DEFAULT_DIRECTORY=" + args.DefaultProjDir + "\n")
    
    # Hardware paths
    SourceFile.write("export HIBRIDA_HARDWARE_PATH=$HIBRIDA_PATH/hardware\n")
    
    # Software paths
    SourceFile.write("export HIBRIDA_SOFTWARE_PATH=$HIBRIDA_PATH/software\n")
    SourceFile.write("export HIBRIDA_APPCOMPOSER_PATH=$HIBRIDA_SOFTWARE_PATH/AppComposer\n")
    SourceFile.write("export HIBRIDA_PLATFORMCOMPOSER_PATH=$HIBRIDA_SOFTWARE_PATH/PlatformComposer\n")
    SourceFile.write("export $PATH=$PATH:$HIBRIDA_APPCOMPOSER_PATH\n")
    SourceFile.write("export $PATH=$PATH:$HIBRIDA_PLATFORMCOMPOSER_PATH\n")
    
    # Flowgen paths
    SourceFile.write("export FLOWGEN_TOPOLOGIES_PATH=" + args.TopologiesPath + "\n")
    SourceFile.write("export FLOWGEN_WORKLOADS_PATH=" + args.WorkloadsPath + "\n")
    SourceFile.write("export FLOWGEN_ALLOCATIONMAPS_PATH=" + args.AllocationMapsPath + "\n")
    SourceFile.write("export FLOWGEN_CLUSTERCLOCKS_PATH=" + args.ClusterClocksPath + "\n")
    
# Creates windows src file
with open(args.InstallName + ".bat", "w") as SourceFile:
    
    # Main paths
    SourceFile.write("set HIBRIDA_NAME=" + args.InstallName + "\n")
    SourceFile.write("set HIBRIDA_PATH=" + args.InstallPath + "\n")
    SourceFile.write("set PATH=%PATH%;%HIBRIDA_PATH%/scripts\n")
    SourceFile.write("doskey " + args.InstallName + "=./" + args.InstallPath + "/scripts/mainScript\n")
    SourceFile.write("set HIBRIDA_DEFAULT_DIRECTORY=" + args.DefaultProjDir + "\n")
    
    # Hardware paths
    SourceFile.write("set HIBRIDA_HARDWARE_PATH=%HIBRIDA_PATH%/hardware\n")
    
    # Software paths
    SourceFile.write("set HIBRIDA_SOFTWARE_PATH=%HIBRIDA_PATH%/software\n")
    SourceFile.write("set HIBRIDA_APPCOMPOSER_PATH=%HIBRIDA_SOFTWARE_PATH%/AppComposer\n")
    SourceFile.write("set HIBRIDA_PLATFORMCOMPOSER_PATH=%HIBRIDA_SOFTWARE_PATH%/PlatformComposer\n")
    SourceFile.write("set PATH=%PATH%;%HIBRIDA_APPCOMPOSER_PATH%\n")
    SourceFile.write("set PATH=%PATH%;%HIBRIDA_PLATFORMCOMPOSER_PATH%\n")
    
    # Flowgen paths
    SourceFile.write("set FLOWGEN_TOPOLOGIES_PATH=" + args.TopologiesPath + "\n")
    SourceFile.write("set FLOWGEN_WORKLOADS_PATH=" + args.WorkloadsPath + "\n")
    SourceFile.write("set FLOWGEN_ALLOCATIONMAPS_PATH=" + args.AllocationMapsPath + "\n")
    SourceFile.write("set FLOWGEN_CLUSTERCLOCKS_PATH=" + args.ClusterClocksPath + "\n")
