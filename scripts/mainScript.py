#!/usr/bin/python
import sys
import os

# Imports command scripts
import Projgen
import Flowgen
import Comp
import Elab
import Sim
import Loganalyser
import Hlp

# TODO: Check if python 3

import argparse

hibridaName = str(os.getenv("HIBRIDA_NAME"))
if hibridaName is None:
    print("Error: Environment variable $HIBRIDA_NAME doesnt exist. Did you source the source file created by the setup script?")
    exit(1)

parser = argparse.ArgumentParser(prog = hibridaName)

parser.add_argument("Command", choices = ["projgen", "flowgen", "compile", "elab", "sim", "loganalyser", "help"], type = str.lower, default = "help", help = "", required = True)

subparsers = parser.add_subparsers(title = "Hibrida commands")

# projgen args
parser_projgen = subparsers.add_parser("projgen", help = "Creates a new hibrida project at a given location")
parser_projgen.add_argument("-d", "-D", "--ProjectDirectory", type = str, default = os.getenv("HIBRIDA_DEFAULT_DIRECTORY"))
parser_projgen.add_argument("-n", "-N", "--ProjectName", type = str, default = "HibridaProject")
#parser_projgen.add_argument("-f", "-F", "--TopologyFile", type = str, default = None)

# flowgen args
parser_flowgen = subparsers.add_parser("flowgen", help = "Generates Injectors' JSON config files, implementing a given Workload")
parser_flowgen.add_argument("-t", "-T", "--TopologyFile", type = str, default = None)
parser_flowgen.add_argument("-w", "-W", "--WorkloadFile", type = str, default = None)
parser_flowgen.add_argument("-a", "-A", "--AllocMapFile", type = str, default = None)
parser_flowgen.add_argument("-c", "-C", "--ClusterClocksFile", type = str, default = None)

if os.getenv("FLOWGEN_TOPOLOGIES_PATH") is not None:
    parser_flowgen.add_argument("-TopologiesPath", type = str, default = os.getenv("FLOWGEN_TOPOLOGIES_PATH"))
else:
    print("Error: Environment variable $FLOWGEN_TOPOLOGIES_PATH doesnt exist. Did you source the source file created by the setup script?")
    exit(1)
    
if os.getenv("FLOWGEN_WORKLOADS_PATH") is not None:
    parser_flowgen.add_argument("-WorkloadsPath", type = str, default = os.getenv("FLOWGEN_WORKLOADS_PATH"))
else:
    print("Error: Environment variable $FLOWGEN_WORKLOADS_PATH doesnt exist. Did you source the source file created by the setup script?")
    exit(1)
    
if os.getenv("FLOWGEN_ALLOCATIONMAPS_PATH") is not None:
    parser_flowgen.add_argument("-AllocationMapsPath", type = str, default = os.getenv("FLOWGEN_ALLOCATIONMAPS_PATH"))
else:
    print("Error: Environment variable $FLOWGEN_ALLOCATIONMAPS_PATH doesnt exist. Did you source the source file created by the setup script?")
    exit(1)
    
if os.getenv("FLOWGEN_CLUSTERCLOCKS_PATH") is not None:    
    parser_flowgen.add_argument("-ClusterClocksPath", type = str, default = os.getenv("FLOWGEN_CLUSTERCLOCKS_PATH"))
else:
    print("Error: Environment variable $FLOWGEN_CLUSTERCLOCKS_PATH doesnt exist. Did you source the source file created by the setup script?")
    exit(1)

# TODO: compile args


# TODO: elab args


# TODO: sim args


# TODO: loganalyser args


args = parser.parse_args()

# Sets dictionary containing function pointers to available commands
scripts = dict()
scripts["projgen"] = Projgen.projgen
scripts["flowgen"] = Flowgen.flowgen
scripts["compile"] = Comp.comp
scripts["elab"] = Elab.elab
scripts["sim"] = Sim.sim
scripts["loganalyser"] = Loganalyser.loganalyser
scripts["help"] = Hlp.hlp

# Executes given command
if args.Command in scripts.keys():
    scripts[args.Command](args)
else:
    scripts["help"]
