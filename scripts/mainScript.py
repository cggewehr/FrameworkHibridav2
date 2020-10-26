#!/usr/bin/python
import sys
import os

# Imports command scripts
import Projgen
import Flowgen
#import Comp
#import Elab
#import Sim
#import Loganalyser

import argparse

if os.getenv("HIBRIDA_NAME") is None:
    print("Error: Environment variable $HIBRIDA_NAME doesnt exist. Did you source the source file created by the setup script?")
    exit(1)

parser = argparse.ArgumentParser(prog = os.getenv("HIBRIDA_NAME"))

#parser.add_argument("Command", type = str.lower, help = "Avaiable subcommands")

subparsers = parser.add_subparsers(title = "Hibrida subcommands")

# projgen args
parser_projgen = subparsers.add_parser("projgen", help = "Creates a new project at a given location")
parser_projgen.set_defaults(func=Projgen.projgen)
parser_projgen.add_argument("--ProjectDirectory", type = str, default = os.getenv("HIBRIDA_DEFAULT_DIRECTORY"))
parser_projgen.add_argument("--ProjectName", type = str, default = "HibridaProject")
parser_projgen.add_argument("--HardwareDirs", help = "Create directories and subdirectories for custom hardware", action="store_true")
parser_projgen.add_argument("--Makefile", type = str, default = "cadence", help = "Create makefile for compile, elab and simulate project")

# TODO: Create project from topology .json file
#parser_projgen.add_argument("-f", "-F", "--TopologyFile", type = str, default = None)

# flowgen args
parser_flowgen = subparsers.add_parser("flowgen", help = "Generates injector JSON config files, implementing a given workload in a given topology")
parser_flowgen.set_defaults(func=Flowgen.flowgen)
parser_flowgen.add_argument("--ProjectDir", type = str, required = True, help = "Path to project's location")
parser_flowgen.add_argument("--TopologyFile", type = str, required = True, help = ".json file containing inteconnect topology information (AmountOfPEs, BusWrapperAddresses, ...)")
parser_flowgen.add_argument("--WorkloadFile", type = str, required = True, help = ".json file containing workload information (Apps & Threads)")
parser_flowgen.add_argument("--AllocMapFile", type = str, required = True, help = ".json file containing Thread to PE mapping information")
parser_flowgen.add_argument("--ClusterClocksFile", type = str, required = True, help = ".json file containing cluster clock frequency information")

# TODO: Add arg so that paths to Topologies, Workloads, AllocMaps and ClusterClocks are infered from a single given diretory, such as <GivenDir>/Topologies, <GivenDir>/Workloads, ...

if os.getenv("FLOWGEN_TOPOLOGIES_PATH") is not None:
    parser_flowgen.add_argument("--TopologiesPath", type = str, default = os.getenv("FLOWGEN_TOPOLOGIES_PATH"))
else:
    print("Error: Environment variable $FLOWGEN_TOPOLOGIES_PATH doesnt exist. Did you run the .source/.bat file created by the setup script?")
    exit(1)
    
if os.getenv("FLOWGEN_WORKLOADS_PATH") is not None:
    parser_flowgen.add_argument("--WorkloadsPath", type = str, default = os.getenv("FLOWGEN_WORKLOADS_PATH"))
else:
    print("Error: Environment variable $FLOWGEN_WORKLOADS_PATH doesnt exist. Did you run the .source/.bat file created by the setup script?")
    exit(1)
    
if os.getenv("FLOWGEN_ALLOCATIONMAPS_PATH") is not None:
    parser_flowgen.add_argument("--AllocationMapsPath", type = str, default = os.getenv("FLOWGEN_ALLOCATIONMAPS_PATH"))
else:
    print("Error: Environment variable $FLOWGEN_ALLOCATIONMAPS_PATH doesnt exist. Did you run the .source/.bat file created by the setup script?")
    exit(1)
    
if os.getenv("FLOWGEN_CLUSTERCLOCKS_PATH") is not None:    
    parser_flowgen.add_argument("--ClusterClocksPath", type = str, default = os.getenv("FLOWGEN_CLUSTERCLOCKS_PATH"))
else:
    print("Error: Environment variable $FLOWGEN_CLUSTERCLOCKS_PATH doesnt exist. Did you run the .source/.bat file created by the setup script?")
    exit(1)

# TODO: compile args
# parser_compile = subparsers.add_parser("compile", help = "Compiles VHDL files with a ")
#supportedTools = ["Cadence", "Vivado", "ISE", "Modelsim"]
#parser_compile.add_argument("ProjectPath", type = str, help = "Path to project to be compiled")
#parser_compile.add_argument("-t", "--tool", type = str, choices = supportedTools, help = "Which tool to compile the project")
# TODO: Make default tcl compilation scripts for each supported tool
# parser_compile.add_argument("-f", "--file", type = str, help = "Custom script file to be executed", default = None)

# TODO: elab args


# TODO: sim args


# TODO: loganalyser args

# Parse args and execute given command
args = parser.parse_args()
args.func(args)
